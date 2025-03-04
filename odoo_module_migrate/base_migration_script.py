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
    _module_path = ""

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
                        rules[rule]["doc"].extend(new_rules)
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
        for root, directories, filenames in os.walk(module_path.resolve()):
            for filename in filenames:
                extension = os.path.splitext(filename)[1]
                if extension not in _ALLOWED_EXTENSIONS:
                    continue
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
        field_renames = renamed_fields.get("replaces")
        # To be safe we only rename fields on files associated with the current replaces
        if field_renames:
            new_text = tools._replace_field_names(
                absolute_file_path,
                field_renames,
                "Updated field names of %s" % filename,
            )

        # Display errors if the new content contains some obsolete
        # pattern
        errors = self._TEXT_ERRORS.get("*", {})
        errors.update(self._TEXT_ERRORS.get(extension, {}))
        errors.update(renamed_models.get("errors"))
        errors.update(removed_models.get("errors"))
        for pattern, error_message in errors.items():
            if re.findall(pattern, new_text):
                logger.error(error_message)

        warnings = self._TEXT_WARNINGS.get("*", {})
        warnings.update(self._TEXT_WARNINGS.get(extension, {}))
        warnings.update(removed_fields.get("warnings"))
        warnings.update(renamed_fields.get("warnings"))
        warnings.update(renamed_models.get("warnings"))
        warnings.update(removed_models.get("warnings"))
        for pattern, warning_message in warnings.items():
            if re.findall(pattern, new_text):
                logger.warning(warning_message + ". File " + root + os.sep + filename)

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
            res[r"""(['"]{0}['"]|\.{0}[\s,=])""".format(field_name)] = msg
        return {"warnings": res}

    def handle_renamed_fields(self, removed_fields):
        """Give warnings if old_field_name is found on the code. To minimize
         two many false positives we search for field name on this situations:
         * with simple/double quotes
         * prefixed with dot and with space, comma or equal after the string
        For now this handler is simple but the idea would be to improve it
        with deeper analysis and direct replaces if it is possible and secure.
        For that analysis model_name could be used
        It also will add to the replaces key of the returned dictionary a key value pair
         to be used in _replace_in_file
        """
        res = {"warnings": {}, "replaces": {}}
        res["replaces"] = {}
        for model_name, old_field_name, new_field_name, more_info in removed_fields:
            # if model_name in res['replaces']:
            #     res['replaces'][model_name].update({old_field_name: new_field_name,})
            # else:
            res["replaces"].update(
                {
                    model_name: {
                        old_field_name: new_field_name,
                    }
                }
            )
            msg = "On the model %s, the field %s was renamed to %s.%s" % (
                model_name,
                old_field_name,
                new_field_name,
                " %s" % more_info if more_info else "",
            )
            res["warnings"].update(
                {
                    r"""(['"]{0}['"]|\.{0}[\s,=])""".format(old_field_name): msg,
                }
            )
        return res

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
