# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import re
from .log import logger

from .config import _ALLOWED_EXTENSIONS
from .tools import _execute_shell


class ModuleMigration():

    _migration = False
    _module_name = False
    _module_path = False

    def __init__(self, migration, module_name):
        self._migration = migration
        self._module_name = module_name
        self._module_path = self._migration._directory_path / module_name

    def run(self):
        logger.info("Running migration of module %s" % self._module_name)
        self._run_black()
        for migration_script in self._migration._migration_scripts:
            self._run_migration_scripts(migration_script)

    def _run_black(self):
        # TODO
        pass

    def _run_migration_scripts(self, migration_script):
        file_renames = getattr(migration_script, "_FILE_RENAMES", {})
        text_replaces = getattr(migration_script, "_TEXT_REPLACES", {})
        text_warnings = getattr(migration_script, "_TEXT_WARNING", {})

        has_change = False

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
                    has_change = True
                    self._rename_file(
                        self._migration._directory_path,
                        absolute_file_path,
                        os.path.join(root, new_name))
                    absolute_file_path = os.path.join(root, new_name)

                with open(absolute_file_path, "U") as f:
                    # Operate changes in the file (replacements, removals)
                    current_text = f.read()
                    new_text = current_text

                    replaces = text_replaces.get("*", {})
                    replaces.update(text_replaces.get(extension, {}))

                    for old_term, new_term in replaces.items():
                        new_text = re.sub(old_term, new_term, new_text)

                    # Write file if changed
                    if new_text != current_text:
                        has_change = True
                        logger.info("Changing content of file: %s" % filename)
                        with open(absolute_file_path, "w") as f:
                            f.write(new_text)

                    # Display warnings if the file contents some obsolete code
                    warnings = text_warnings.get("*", {})
                    warnings.update(text_warnings.get(extension, {}))
                    for pattern, warning_message in warnings.items():
                        if re.findall(pattern, new_text):
                            logger.warning(warning_message)

        # Commit changes
        if has_change:
            commit_name = "[MIG] %s: Migration to %s" % (
                self._module_name,
                self._migration._migration_steps[-1]["target_version_name"])

            logger.info(
                "Commit changes for %s. commit name '%s'" % (
                    self._module_name, commit_name
                ))

            _execute_shell(
                "cd %s && git add . --all && git commit -m '%s'" % (
                    str(self._migration._directory_path.resolve()), commit_name
                ))

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

        _execute_shell(
            "cd %s && git mv %s %s" % (
                str(module_path.resolve()), old_file_path, new_file_path
            ))
