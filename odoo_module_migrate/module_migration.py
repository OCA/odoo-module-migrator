# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from .log import logger

from .config import _MANIFEST_NAMES
from .tools import _execute_shell


class ModuleMigration:

    _migration = False
    _module_name = False
    _module_path = False

    def __init__(self, migration, module_name):
        self._migration = migration
        self._module_name = module_name
        self._module_path = self._migration._directory_path / module_name

    def run(self):
        logger.info(
            "[%s] Running migration from %s to %s"
            % (
                self._module_name,
                self._migration._migration_steps[0]["init_version_name"],
                self._migration._migration_steps[-1]["target_version_name"],
            )
        )

        # Apply migration script
        for migration_script in self._migration._migration_scripts:
            migration_script.run(
                self._module_path,
                self._get_manifest_path(),
                self._module_name,
                self._migration._migration_steps,
                self._migration._directory_path,
                self._migration._commit_enabled,
            )

        # Run pre-commit before final commit to format any changes made during migration scripts execution
        if os.path.exists(".pre-commit-config.yaml") and self._migration._pre_commit:
            _execute_shell(
                "pre-commit run -a",
                path=self._migration._directory_path,
                raise_error=False,
            )

        self._commit_changes(
            "[MIG] %s: Migration to %s"
            % (
                self._module_name,
                self._migration._migration_steps[-1]["target_version_name"],
            )
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
            "Renaming file: '%s' by '%s' "
            % (
                old_file_path.replace(str(module_path.resolve()), ""),
                new_file_path.replace(str(module_path.resolve()), ""),
            )
        )
        if self._migration._commit_enabled:
            _execute_shell(
                "git mv %s %s" % (old_file_path, new_file_path), path=module_path
            )
        else:
            _execute_shell(
                "mv %s %s" % (old_file_path, new_file_path), path=module_path
            )

    def _commit_changes(self, commit_name):
        if not self._migration._commit_enabled:
            return

        if _execute_shell("git diff", path=self._migration._directory_path):
            logger.info(
                "Commit changes for %s. commit name '%s'"
                % (self._module_name, commit_name)
            )

            _execute_shell(
                " git add . --all && git commit --no-verify -m '%s'" % (commit_name),
                path=self._migration._directory_path,
            )
