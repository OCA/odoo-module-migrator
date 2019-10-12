# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import black
import os
import pathlib
import re
from .log import logger

from .config import _ALLOWED_EXTENSIONS, _BLACK_LINE_LENGTH, _MANIFEST_NAMES
from .tools import _execute_shell
from . import tools


class ModuleMigration():

    _migration = False
    _module_name = False
    _module_path = False

    def __init__(self, migration, module_name):
        self._migration = migration
        self._module_name = module_name
        self._module_path = self._migration._directory_path / module_name

    def run(self):
        logger.info("[%s] Running migration from %s to %s" % (
            self._module_name,
            self._migration._migration_steps[0]["init_version_name"],
            self._migration._migration_steps[-1]["target_version_name"],
        ))

        # Run Black, if required
        self._run_black()
        self._commit_changes(
            "[REF] %s: Black python code" % (self._module_name))

        # Apply migration script
        for migration_script in self._migration._migration_scripts:
            self._run_migration_scripts(migration_script)

        # Rerun black, to avoid that automated changes broke black rules
        self._run_black()
        self._commit_changes("[MIG] %s: Migration to %s" % (
            self._module_name,
            self._migration._migration_steps[-1]["target_version_name"]))

    def _run_black(self):
        if not self._migration._use_black:
            return

        file_mode = black.FileMode()
        file_mode.line_length = _BLACK_LINE_LENGTH

        for root, directories, filenames in os.walk(
                self._module_path.resolve()):
            for filename in filenames:
                # Skip useless file
                if os.path.splitext(filename)[1] != ".py":
                    continue

                absolute_file_path = os.path.join(root, filename)

                black.format_file_in_place(
                    pathlib.Path(absolute_file_path), False, file_mode,
                    black.WriteBack.YES)

    def _run_migration_scripts(self, migration_script):
        file_renames = getattr(migration_script, "_FILE_RENAMES", {})
        text_replaces = getattr(migration_script, "_TEXT_REPLACES", {})
        text_errors = getattr(migration_script, "_TEXT_ERRORS", {})
        global_functions = getattr(migration_script, "_GLOBAL_FUNCTIONS", {})
        deprecated_modules = getattr(
            migration_script, "_DEPRECATED_MODULES", {})

        for root, directories, filenames in os.walk(
                self._module_path.resolve()):
            for filename in filenames:
                # Skip useless file
                # TODO, skip files present in some folders. (for exemple 'lib')
                extension = os.path.splitext(filename)[1]
                if extension not in _ALLOWED_EXTENSIONS:
                    continue

                absolute_file_path = os.path.join(root, filename)
                logger.debug("Migrate '%s' file" % absolute_file_path)

                # Rename file, if required
                new_name = file_renames.get(filename)
                if new_name:
                    self._rename_file(
                        self._migration._directory_path,
                        absolute_file_path,
                        os.path.join(root, new_name))
                    absolute_file_path = os.path.join(root, new_name)

                # Operate changes in the file (replacements, removals)
                replaces = text_replaces.get("*", {})
                replaces.update(text_replaces.get(extension, {}))

                new_text = tools._replace_in_file(
                    absolute_file_path, replaces,
                    "Change file content of %s" % filename)

                # Display errors if the new content contains some obsolete
                # pattern
                errors = text_errors.get("*", {})
                errors.update(text_errors.get(extension, {}))
                for pattern, error_message in errors.items():
                    if re.findall(pattern, new_text):
                        logger.error(error_message)

        # Handle deprecated modules
        current_manifest_text = tools._read_content(self._get_manifest_path())
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

            if action == 'removed':
                # The module has been removed, just log an error.
                logger.error(
                    "Depends on removed module '%s'" % (old_module))

            elif action == 'renamed':
                new_manifest_text = re.sub(
                    old_module_pattern, replace_pattern, new_manifest_text)
                logger.info(
                    "Replaced dependency of '%s' by '%s'." % (
                        old_module, new_module))

            elif action == 'oca_moved':
                new_manifest_text = re.sub(
                    old_module_pattern, replace_pattern, new_manifest_text)
                logger.warning(
                    "Replaced dependency of '%s' by '%s' (%s)\n"
                    "Check that '%s' is available on your system." % (
                        old_module, new_module, items[3], new_module))

            elif action == "merged":
                if not re.findall(new_module_pattern, new_manifest_text):
                    # adding dependency of the merged module
                    new_manifest_text = re.sub(
                        old_module_pattern, replace_pattern, new_manifest_text)
                    logger.info(
                        "'%s' merged in '%s'. Replacing dependency." % (
                            old_module, new_module))
                else:
                    # TODO, improve me. we should remove the dependency
                    # but it could generate coma trouble.
                    # maybe handling this treatment by ast lib could fix
                    # the problem.
                    logger.error(
                        "'%s' merged in '%s'. You should remove the"
                        " dependency to '%s' manually." % (
                            old_module, new_module, old_module))

        if current_manifest_text != new_manifest_text:
            tools._write_content(self._get_manifest_path(), new_manifest_text)

        if global_functions:
            for function in global_functions:
                function(
                    logger=logger,
                    module_path=self._module_path,
                    module_name=self._module_name,
                    manifest_path=self._get_manifest_path(),
                    migration_steps=self._migration._migration_steps,
                    tools=tools,
                )

    def _get_manifest_path(self):
        for manifest_name in _MANIFEST_NAMES:
            manifest_path = self._module_path / manifest_name
            if manifest_path.exists():
                return manifest_path

    def _rename_file(self, module_path, old_file_path, new_file_path):
        """
        Rename a file. try to execute 'git mv', to avoid huge diff.

        if 'git mv' fails, make a classical rename
        """
        logger.info(
            "Renaming file: '%s' by '%s' " % (
                old_file_path.replace(str(module_path.resolve()), ""),
                new_file_path.replace(str(module_path.resolve()), ""))
        )
        if self._migration._commit_enabled:
            _execute_shell(
                "cd %s && git mv %s %s" % (
                    str(module_path.resolve()), old_file_path, new_file_path
                ))
        else:
            _execute_shell(
                "cd %s && mv %s %s" % (
                    str(module_path.resolve()), old_file_path, new_file_path
                ))

    def _commit_changes(self, commit_name):
        if not self._migration._commit_enabled:
            return

        if _execute_shell("cd %s && git diff" % (
                str(self._migration._directory_path.resolve()))):
            logger.info(
                "Commit changes for %s. commit name '%s'" % (
                    self._module_name, commit_name
                ))

            _execute_shell(
                "cd %s && git add . --all && git commit -m '%s'" % (
                    str(self._migration._directory_path.resolve()), commit_name
                ))
