import os
from .config import _ALLOWED_EXTENSIONS
from .tools import _execute_shell
from .log import logger
from . import tools
import re
import pathlib
import traceback
import inspect
import glob
import yaml
import importlib
import requests
from tqdm import tqdm
from .ai_migration_helper import AIMigrationHelper


class BaseMigrationScript(object):
    _TEXT_REPLACES = {}
    _TEXT_ERRORS = {}
    _TEXT_WARNINGS = {}
    _DEPRECATED_MODULES = []
    _FILE_RENAMES = {}
    _REMOVED_FIELDS = []
    _RENAMED_FIELDS = []
    _RENAMED_MODELS = []
    _REMOVED_MODELS = []
    _GLOBAL_FUNCTIONS = []  # [function_object]
    _AI_TRANSFORMS = []
    _module_path = ""

    def __init__(self):
        self._warnings_by_message = {}
        self._errors_by_message = {}
        self._repo_root = None
        self._ai_helper = AIMigrationHelper()

    def _get_controller_data(self, version_from_to):
        # data = request.get(url, version_from, version_to)
        # version_from_to:
        #     - migrate_100_allways.py
        #     - migrate_160_170.py
        #     - migrate_allways.py
        # [0] - migrate
        # [1] - version_from
        # [2] - version_to
        list_version_from_to = version_from_to.split("_")
        if len(list_version_from_to) != 3 or "allways" in list_version_from_to:
            return False
        version_from = list_version_from_to[1]
        version_to = list_version_from_to[2]
        return self._get_changes_from_adhoc(version_from, version_to)

    def _get_changes_from_adhoc(self, init_version_name, target_version_name):
        base_url = os.getenv("ADHOC_URL", False)
        if not base_url:
            logger.warning("No ADHOC_URL env variable found. Version Changes skipped")
            return False
        endpoint = "/version_changes/{from_version}/{to_version}".format(
            from_version=init_version_name, to_version=target_version_name
        )
        uri = base_url + endpoint
        self._requests = requests.Session()
        response = self._requests.get(uri)

        if response and response.ok:
            data_version_changes = response.json()
            return data_version_changes
        return False

    def parse_rules(self):
        script_parts = inspect.getfile(self.__class__).split("/")
        migrate_from_to = script_parts[-1].split(".")[0]
        migration_scripts_dir = "/".join(script_parts[:-1])

        TYPE_ARRAY = "TYPE_ARRAY"
        TYPE_DICT = "TYPE_DICT"
        TYPE_DICT_OF_DICT = "TYPE_DICT_OF_DICT"
        rules = {
            # {filetype: {regex: replacement}}
            "_TEXT_REPLACES": {
                "type": TYPE_DICT_OF_DICT,
                "doc": {},
            },
            # {filetype: {regex: message}}
            "_TEXT_ERRORS": {
                "type": TYPE_DICT_OF_DICT,
                "doc": {},
            },
            # {filetype: {regex: message}}
            "_TEXT_WARNINGS": {
                "type": TYPE_DICT_OF_DICT,
                "doc": {},
            },
            # [(module, why, ...)]
            "_DEPRECATED_MODULES": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
            # {old_name: new_name}
            "_FILE_RENAMES": {
                "type": TYPE_DICT,
                "doc": {},
            },
            # [(model_name, field_name, more_info), ...)]
            "_REMOVED_FIELDS": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
            # [(model_name, old_field_name, new_field_name, more_info), ...)]
            "_RENAMED_FIELDS": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
            # [(old.model.name, new.model.name, more_info)]
            "_RENAMED_MODELS": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
            # [(old.model.name, more_info)]
            "_REMOVED_MODELS": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
            # [([regex_patterns], prompt), ...]
            "_AI_TRANSFORMS": {
                "type": TYPE_ARRAY,
                "doc": [],
            },
        }
        # read
        for rule in rules.keys():
            rule_folder = rule[1:].lower()
            file_pattern = "%s/%s/%s/*.yaml" % (
                migration_scripts_dir,
                rule_folder,
                migrate_from_to,
            )
            for filename in glob.glob(file_pattern):
                with open(filename) as f:
                    new_rules = yaml.safe_load(f)
                    if rules[rule]["type"] == TYPE_DICT_OF_DICT:
                        for f_type, data in new_rules.items():
                            if f_type not in rules[rule]["doc"]:
                                rules[rule]["doc"][f_type] = {}
                            rules[rule]["doc"][f_type].update(data)
                    elif rules[rule]["type"] == TYPE_DICT:
                        rules[rule]["doc"].update(new_rules)
                    elif rules[rule]["type"] == TYPE_ARRAY:
                        if rule == "_AI_TRANSFORMS":
                            # Convert YAML format to expected tuple format
                            for ai_transform_item in new_rules:
                                extensions = ai_transform_item.get("extensions", [])
                                patterns = ai_transform_item.get("patterns", [])
                                prompt = ai_transform_item.get("prompt", "")
                                rules[rule]["doc"].append(
                                    (extensions, patterns, prompt)
                                )
                        else:
                            rules[rule]["doc"].extend(new_rules)

        # Read from controller
        data_version_changes = self._get_controller_data(migrate_from_to)
        if data_version_changes:
            for change in data_version_changes.values():
                # {'2': {
                #     'change_type': 'rename',
                #     'major_version_id': '17.0',
                #     'model': False,
                #     'field': False,
                #     'model_type': 'model',
                #     'old_name': 'mail.channel',
                #     'new_name': 'discuss.channel',
                #     'notes': '<p>Más información sobre este cambio <a href="https://github.com/odoo/odoo/pull/118354/" target="_blank">en PR 118354</a></p>'
                #     }
                # }

                if (
                    change["change_type"] == "rename"
                    and change["model_type"] == "model"
                ):
                    # [(old.model.name, new.model.name, more_info)]
                    new_rules = [
                        [change["old_name"], change["new_name"], change["notes"]]
                    ]
                    rules["_RENAMED_MODELS"]["doc"].extend(new_rules)

                if (
                    change["change_type"] == "rename"
                    and change["model_type"] == "field"
                ):
                    # [(model_name, old_field_name, new_field_name, more_info), ...)]
                    new_rules = [
                        [
                            change["model"],
                            change["old_name"],
                            change["new_name"],
                            change["notes"],
                        ]
                    ]
                    rules["_RENAMED_FIELDS"]["doc"].extend(new_rules)

                if (
                    change["change_type"] == "remove"
                    and change["model_type"] == "model"
                ):
                    # [(old.model.name, more_info)]
                    new_rules = [[change["old_name"], change["notes"]]]
                    rules["_REMOVED_MODELS"]["doc"].extend(new_rules)

                if (
                    change["change_type"] == "remove"
                    and change["model_type"] == "field"
                ):
                    # [(model_name, field_name, more_info), ...)]
                    new_rules = [[change["model"], change["old_name"], change["notes"]]]
                    rules["_REMOVED_FIELDS"]["doc"].extend(new_rules)

                if (
                    change["change_type"] == "rename"
                    and change["model_type"] == "xmlid"
                ):
                    # [(model_name, old_field_name, new_field_name, more_info), ...)]
                    new_rules = [
                        [
                            change["model"],
                            change["old_name"],
                            change["new_name"],
                            change["notes"],
                        ]
                    ]
                    warnings = rules["_TEXT_REPLACES"]["doc"].get("*", {})
                    warnings[change["old_name"]] = change["new_name"]
                    rules["_TEXT_REPLACES"]["doc"]["*"] = warnings

                if (
                    change["change_type"] == "remove"
                    and change["model_type"] == "xmlid"
                ):
                    # [(model_name, field_name, more_info), ...)]
                    warnings = rules["_TEXT_WARNINGS"]["doc"].get("*", {})
                    warnings[change["old_name"]] = change["notes"]
                    rules["_TEXT_WARNINGS"]["doc"]["*"] = warnings

                if (
                    change["change_type"] == "change_type"
                    and change["model_type"] == "field"
                ):
                    warnings = rules["_TEXT_WARNINGS"]["doc"].get(".py", {})
                    model_info = (
                        f"On the model {change['model']} "
                        if change.get("model")
                        else ""
                    )
                    field_info = (
                        f"for field {change['field']} " if change.get("field") else ""
                    )
                    warnings[change["field"]] = (
                        model_info + field_info + change["notes"]
                    )
                    rules["_TEXT_WARNINGS"]["doc"][".py"] = warnings

                if (
                    change["change_type"] == "remove"
                    and change["model_type"] == "selection_value"
                ):
                    warnings = rules["_TEXT_WARNINGS"]["doc"].get("*", {})
                    model_info = (
                        f"On the model {change['model']} "
                        if change.get("model")
                        else ""
                    )
                    field_info = (
                        f"for field {change['field']} " if change.get("field") else ""
                    )
                    warnings[change["old_name"]] = (
                        model_info + field_info + change["notes"]
                    )
                    rules["_TEXT_WARNINGS"]["doc"]["*"] = warnings

        # extend
        for rule, data in rules.items():
            rtype = data["type"]
            doc = data.get("doc")
            if not doc:
                continue

            rvalues = getattr(self, rule)
            if rtype == TYPE_ARRAY:
                rvalues.extend(doc)
            elif rtype == TYPE_DICT:
                rvalues.update(doc)
            else:
                # TYPE_DICT_OF_DICT
                for filetype, values in doc.items():
                    rvalues.setdefault(filetype, {})
                    rvalues[filetype].update(values or {})

        file_pattern = "%s/python_scripts/%s/*.py" % (
            migration_scripts_dir,
            migrate_from_to,
        )
        for path in glob.glob(file_pattern):
            module_name = path.split("/")[-1].split(".")[0]
            module_name = ".".join(
                [
                    "odoo_module_migrate.migration_scripts.python_scripts",
                    migrate_from_to,
                    module_name,
                ]
            )
            module = importlib.import_module(module_name)
            for name, value in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_"):
                    self._GLOBAL_FUNCTIONS.append(value)

    def run(
        self,
        module_path,
        manifest_path,
        module_name,
        migration_steps,
        directory_path,
        commit_enabled,
    ):
        logger.debug(
            "Running %s script" % inspect.getfile(self.__class__).split("/")[-1]
        )
        self.parse_rules()
        manifest_path = self._get_correct_manifest_path(
            manifest_path, self._FILE_RENAMES
        )
        self._warnings_by_message = {}
        self._repo_root = str(module_path.resolve())

        all_files = []
        for root, directories, filenames in os.walk(module_path.resolve()):
            if 'migrations' in root.split(os.sep):
                continue
            for filename in filenames:
                extension = os.path.splitext(filename)[1]
                if extension in _ALLOWED_EXTENSIONS:
                    all_files.append((root, filename, extension))

        if not (os.getenv("PROGRESS_DISABLE", "0") == "1"):
            all_files = tqdm(all_files, desc="Processing files")

        for root, filename, extension in all_files:
            self.process_file(
                root,
                filename,
                extension,
                self._FILE_RENAMES,
                directory_path,
                commit_enabled,
            )

        self.handle_deprecated_modules(manifest_path, self._DEPRECATED_MODULES)

        if self._GLOBAL_FUNCTIONS:
            for function in self._GLOBAL_FUNCTIONS:
                function(
                    logger=logger,
                    module_path=module_path,
                    module_name=module_name,
                    manifest_path=manifest_path,
                    migration_steps=migration_steps,
                    tools=tools,
                )

        for error_message, files in self._errors_by_message.items():
            rel_files = [os.path.relpath(f, self._repo_root) for f in sorted(files)]
            logger.error("%s\n  %s" % (error_message, "\n  ".join(rel_files)))

        for warning_message, files in self._warnings_by_message.items():
            rel_files = [os.path.relpath(f, self._repo_root) for f in sorted(files)]
            logger.warning("%s\n  %s" % (warning_message, "\n  ".join(rel_files)))

        for (
            filename,
            line_start,
            line_end,
        ), suggestion in self._ai_helper.suggestions.items():
            logger.info(
                "AI Suggestion for %s (lines %d-%d):\n\n%s"
                % (filename, line_start, line_end, suggestion)
            )

        self._ai_helper.suggestions.clear()

    def process_file(
        self, root, filename, extension, file_renames, directory_path, commit_enabled
    ):
        # Skip useless file
        # TODO, skip files present in some folders. (for exemple 'lib')
        absolute_file_path = os.path.join(root, filename)
        logger.debug("Migrate '%s' file" % absolute_file_path)

        # Rename file, if required
        new_name = file_renames.get(filename)
        if new_name:
            self._rename_file(
                directory_path,
                absolute_file_path,
                os.path.join(root, new_name),
                commit_enabled,
            )
            absolute_file_path = os.path.join(root, new_name)

        removed_fields = self.handle_removed_fields(self._REMOVED_FIELDS)
        renamed_fields = self.handle_renamed_fields(self._RENAMED_FIELDS)
        renamed_models = self.handle_renamed_models(self._RENAMED_MODELS)
        removed_models = self.handle_removed_models(self._REMOVED_MODELS)

        # Operate changes in the file (replacements, removals)
        replaces = self._TEXT_REPLACES.get("*", {})
        replaces.update(self._TEXT_REPLACES.get(extension, {}))
        replaces.update(renamed_models.get("replaces"))
        replaces.update(removed_models.get("replaces"))

        new_text = tools._replace_in_file(
            absolute_file_path, replaces, "Change file content of %s" % filename
        )

        # Display errors if the new content contains some obsolete
        # pattern
        errors = self._TEXT_ERRORS.get("*", {})
        errors.update(self._TEXT_ERRORS.get(extension, {}))
        errors.update(renamed_models.get("errors"))
        errors.update(removed_models.get("errors"))
        for pattern, error_message in errors.items():
            if re.findall(pattern, new_text):
                file_path = os.path.join(root, filename)
                self._errors_by_message.setdefault(error_message, set()).add(file_path)

        warnings = self._TEXT_WARNINGS.get("*", {})
        warnings.update(self._TEXT_WARNINGS.get(extension, {}))
        warnings.update(removed_fields.get("warnings"))
        warnings.update(renamed_fields.get("warnings"))
        warnings.update(renamed_models.get("warnings"))
        warnings.update(removed_models.get("warnings"))
        for pattern, warning_message in warnings.items():
            if re.findall(pattern, new_text):
                file_path = os.path.join(root, filename)
                self._warnings_by_message.setdefault(warning_message, set()).add(
                    file_path
                )

        if extension == ".py":
            tools.analyze_field_changes(
                absolute_file_path,
                self._RENAMED_FIELDS,
                self._REMOVED_FIELDS,
                self._warnings_by_message,
            )

        self._ai_helper.apply_ai_transforms(
            filename, extension, content=new_text, ai_transforms=self._AI_TRANSFORMS
        )

    def handle_removed_fields(self, removed_fields):
        """Give warnings if field_name is found on the code. To minimize two
        many false positives we search for field name on this situations:
         * with simple/double quotes
         * prefixed with dot and with space, comma or equal after the string
        For now this handler is simple but the idea would be to improve it
        with deeper analysis and direct replaces if it is possible and secure.
        For that analysis model_name could be used
        """
        res = {}
        for model_name, field_name, more_info in removed_fields:
            msg = "On the model %s, the field %s was deprecated.%s" % (
                model_name,
                field_name,
                " %s" % more_info if more_info else "",
            )
            res[
                r"""(?<!self\.)(?<!self\.write\(\{{)(?<!self\.create\(\{{)(['"]{0}['"]|\.{0}[\s,=])""".format(
                    field_name
                )
            ] = msg
        return {"warnings": res}

    def handle_renamed_fields(self, removed_fields):
        """Give warnings if old_field_name is found on the code. To minimize
         two many false positives we search for field name on this situations:
         * with simple/double quotes
         * prefixed with dot and with space, comma or equal after the string
        For now this handler is simple but the idea would be to improve it
        with deeper analysis and direct replaces if it is possible and secure.
        For that analysis model_name could be used
        """
        res = {}
        for model_name, old_field_name, new_field_name, more_info in removed_fields:
            msg = "On the model %s, the field %s was renamed to %s.%s" % (
                model_name,
                old_field_name,
                new_field_name,
                " %s" % more_info if more_info else "",
            )
            res[
                r"""(?<!self\.)(?<!self\.write\(\{{)(?<!self\.create\(\{{)(['"]{0}['"]|\.{0}[\s,=])""".format(
                    old_field_name
                )
            ] = msg
        return {"warnings": res}

    def handle_deprecated_modules(self, manifest_path, deprecated_modules):
        current_manifest_text = tools._read_content(manifest_path)
        new_manifest_text = current_manifest_text
        for items in deprecated_modules:
            old_module, action = items[0:2]
            new_module = len(items) > 2 and items[2]
            old_module_pattern = r"('|\"){0}('|\")".format(old_module)
            if new_module:
                new_module_pattern = r"('|\"){0}('|\")".format(new_module)
                replace_pattern = r"\1{0}\2".format(new_module)

            if not re.findall(old_module_pattern, new_manifest_text):
                continue

            if action == "removed":
                # The module has been removed, just log an error.
                logger.error("Depends on removed module '%s'" % (old_module))

            elif action == "renamed":
                new_manifest_text = re.sub(
                    old_module_pattern, replace_pattern, new_manifest_text
                )
                logger.info(
                    "Replaced dependency of '%s' by '%s'." % (old_module, new_module)
                )

            elif action == "oca_moved":
                new_manifest_text = re.sub(
                    old_module_pattern, replace_pattern, new_manifest_text
                )
                logger.warning(
                    "Replaced dependency of '%s' by '%s' (%s)\n"
                    "Check that '%s' is available on your system."
                    % (old_module, new_module, items[3], new_module)
                )

            elif action == "merged":
                if not re.findall(new_module_pattern, new_manifest_text):
                    # adding dependency of the merged module
                    new_manifest_text = re.sub(
                        old_module_pattern, replace_pattern, new_manifest_text
                    )
                    logger.info(
                        "'%s' merged in '%s'. Replacing dependency."
                        % (old_module, new_module)
                    )
                else:
                    # TODO, improve me. we should remove the dependency
                    # but it could generate coma trouble.
                    # maybe handling this treatment by ast lib could fix
                    # the problem.
                    logger.error(
                        "'%s' merged in '%s'. You should remove the"
                        " dependency to '%s' manually."
                        % (old_module, new_module, old_module)
                    )
        if current_manifest_text != new_manifest_text:
            tools._write_content(manifest_path, new_manifest_text)

    def handle_renamed_models(self, renamed_models):
        """renamed_models = [(old.model, new.model, msg)]
        returns dictionary of all replaces / warnings / errors produced
        by a model renamed
        {
            'replaces':
                {
                    "old_model_name", 'old_model_name': new_model_name
                    old_table_name["',]: new_table_name["',]
                },
            'warnings':
                {
                    old.model.name: warning msg
                    old_model_name: warning msg
                }
        }
        """
        res = {"replaces": {}, "warnings": {}, "errors": {}}
        for old_model_name, new_model_name, more_info in renamed_models:
            old_table_name = old_model_name.replace(".", "_")
            new_table_name = new_model_name.replace(".", "_")
            old_name_esc = re.escape(old_model_name)
            res["replaces"].update(
                {
                    r"\"%s\"" % old_name_esc: '"%s"' % new_model_name,
                    r"\'%s\'" % old_name_esc: "'%s'" % new_model_name,
                    r"\"%s\"" % old_table_name: '"%s"' % new_table_name,
                    r"\'%s\'" % old_table_name: "'%s'" % new_table_name,
                    r"model_%s\"" % old_table_name: 'model_%s"' % new_table_name,
                    r"model_%s\'" % old_table_name: "model_%s'" % new_table_name,
                    r"model_%s," % old_table_name: "model_%s," % new_table_name,
                }
            )
            msg = "The model %s has been renamed to %s.%s" % (
                old_model_name,
                new_model_name,
                (" %s" % more_info) or "",
            )
            res["warnings"].update(
                {
                    old_name_esc: msg,
                    old_table_name: msg,
                }
            )
        return res

    def handle_removed_models(self, removed_models):
        """removed_models = [(old.model, msg)]
        returns dictionary of all replaces / warnings / errors produced
        by a model renamed
        {
            'error':
                {
                    "old_model_name", 'old_model_name': new_model_name
                    old_table_name["',]: new_table_name["',]
                },
            'warnings':
                {
                    old.model.name: warning msg
                    old_model_name: warning msg
                }
        }
        """
        res = {"replaces": {}, "warnings": {}, "errors": {}}
        for model_name, more_info in removed_models:
            table_name = model_name.replace(".", "_")
            model_name_esc = re.escape(model_name)

            msg = "The model %s has been deprecated.%s" % (
                model_name,
                (" %s" % more_info) or "",
            )

            res["errors"].update(
                {
                    r"\"%s\"" % model_name_esc: msg,
                    r"\'%s\'" % model_name_esc: msg,
                    r"\"%s\"" % table_name: msg,
                    r"\'%s\'" % table_name: msg,
                    r"model_%s\"" % table_name: msg,
                    r"model_%s\'" % table_name: msg,
                    r"model_%s," % table_name: msg,
                }
            )
            res["warnings"].update(
                {
                    model_name_esc: msg,
                    table_name: msg,
                }
            )
        return res

    def _get_correct_manifest_path(self, manifest_path, file_renames):
        current_manifest_file_name = manifest_path.as_posix().split("/")[-1]
        if current_manifest_file_name in file_renames:
            new_manifest_file_name = manifest_path.as_posix().replace(
                current_manifest_file_name, file_renames[current_manifest_file_name]
            )
            manifest_path = pathlib.Path(new_manifest_file_name)
        return manifest_path

    def _rename_file(self, module_path, old_file_path, new_file_path, commit_enabled):
        """
        Rename a file. try to execute 'git mv', to avoid huge diff.

        if 'git mv' fails, make a classical rename
        """
        logger.info(
            "Renaming file: '%s' by '%s' "
            % (
                old_file_path.replace(str(module_path.resolve()), ""),
                new_file_path.replace(str(module_path.resolve()), ""),
            )
        )
        try:
            if commit_enabled:
                _execute_shell(
                    "git mv %s %s" % (old_file_path, new_file_path), path=module_path
                )
            else:
                _execute_shell(
                    "mv %s %s" % (old_file_path, new_file_path), path=module_path
                )
        except BaseException:
            logger.error(traceback.format_exc())
