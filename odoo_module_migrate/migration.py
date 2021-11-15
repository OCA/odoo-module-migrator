# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import click
import importlib
import os
import pathlib
import pkgutil
import inspect

from .config import _AVAILABLE_MIGRATION_STEPS, _MANIFEST_NAMES
from .exception import ConfigException, CommandException
from .log import logger
from .tools import _execute_shell, _get_latest_version_code
from .module_migration import ModuleMigration
from .base_migration_script import BaseMigrationScript


class Migration:

    def __init__(
        self, relative_directory_path, init_version_name, target_version_name,
        module_names=None, format_patch=False, remote_name='origin',
        commit_enabled=True, pre_commit=True, remove_migration_folder=True,
    ):
        if not module_names:
            module_names = []
        self._commit_enabled = commit_enabled
        self._pre_commit = pre_commit
        self._remove_migration_folder = remove_migration_folder
        self._migration_steps = []
        self._migration_scripts = []
        self._module_migrations = []
        self._directory_path = False

        # Get migration steps that will be runned
        found = False
        for item in _AVAILABLE_MIGRATION_STEPS:
            if not found and item["init_version_name"] != init_version_name:
                continue
            else:
                found = True
            self._migration_steps.append(item)
            if item["target_version_name"] == target_version_name:
                # This is the last step, exiting
                break

        # Check consistency between format patch and module_names args
        if format_patch and len(module_names) != 1:
            raise ConfigException(
                "Format patch option can only be used for a single module")
        logger.debug("Module list: %s" % module_names)
        logger.debug("format patch option : %s" % format_patch)

        # convert relative or absolute directory into Path Object
        if not os.path.exists(relative_directory_path):
            raise ConfigException(
                "Unable to find directory: %s" % relative_directory_path)

        root_path = pathlib.Path(relative_directory_path)
        self._directory_path = pathlib.Path(root_path.resolve(strict=True))

        # format-patch, if required
        if format_patch:
            if not (root_path / module_names[0]).is_dir():
                self._get_code_from_previous_branch(
                    module_names[0], remote_name)
            else:
                logger.warning(
                    "Ignoring format-patch argument, as the module %s"
                    " is still present in the repository" % (module_names[0]))

        # Guess modules if not provided, and check validity
        if not module_names:
            module_names = []
            # Recover all submodules, if no modules list is provided
            child_paths = [x for x in root_path.iterdir() if x.is_dir()]
            for child_path in child_paths:
                if self._is_module_path(child_path):
                    module_names.append(child_path.name)
        else:
            child_paths = [root_path / x for x in module_names]
            for child_path in child_paths:
                if not self._is_module_path(child_path):
                    module_names.remove(child_path.name)
                    logger.warning(
                        "No valid module found for '%s' in the directory '%s'"
                        % (child_path.name, root_path.resolve()))

        if not module_names:
            raise ConfigException("No modules found to migrate. Exiting.")

        for module_name in module_names:
            self._module_migrations.append(ModuleMigration(self, module_name))

        if os.path.exists(".pre-commit-config.yaml") and self._pre_commit:
            self._run_pre_commit(module_names)

        # get migration scripts, depending to the migration list
        self._get_migration_scripts()

    def _execute_shell(self, shell_command, **kwargs):
        """Helper to execute shell commands in the directory_path"""
        if "path" not in kwargs:
            kwargs["path"] = self._directory_path
        return _execute_shell(shell_command, **kwargs)

    def _run_pre_commit(self, module_names):
        logger.info("Run pre-commit")
        self._execute_shell("pre-commit run -a", raise_error=False)
        if self._commit_enabled:
            logger.info("Stage and commit changes done by pre-commit")
            self._execute_shell("git add -A")
            self._execute_shell(
                "git commit -m '[IMP] %s: pre-commit execution' --no-verify"
                % ", ".join(module_names),
                raise_error=False,  # Don't fail if there is nothing to commit
            )

    def _is_module_path(self, module_path):
        return any([(module_path / x).exists() for x in _MANIFEST_NAMES])

    def _create_migration_branch(self, module_name, remote_name):
        """Creates the migration branch"""
        target_version = self._migration_steps[-1]["target_version_name"]
        branch_name = "{version}-mig-{module_name}".format(
            version=target_version, module_name=module_name
        )
        logger.info(f"Creating new branch '{branch_name}' ...")
        if self._execute_shell(f"git branch --list {branch_name}"):
            msg = (
                "Branch %(branch)s already exists.\n"
                "Do you want to recreate it? ⚠️  "
                "You will lose the existing branch."
                % {
                    "branch": branch_name
                }
            )
            if click.confirm(msg):
                self._execute_shell(f"git branch -D {branch_name}")
            else:
                raise CommandException(
                    f"Branch '{branch_name}' already exists. Aborting..."
                )
        self._execute_shell(
            "git checkout --no-track -b %(branch)s %(remote)s/%(version)s" % {
                "branch": branch_name,
                "remote": remote_name,
                "version": target_version,
            }
        )

    def _get_code_from_previous_branch(self, module_name, remote_name):
        init_version = self._migration_steps[0]["init_version_name"]
        target_version = self._migration_steps[-1]["target_version_name"]
        self._create_migration_branch(module_name, remote_name)

        logger.info("Getting latest changes from old branch")
        # Depth is added just in case you had a shallow git history
        self._execute_shell(
            "git fetch --depth 9999999 %(remote)s %(init)s" % {
                'remote': remote_name,
                'init': init_version,
            }
        )
        self._execute_shell(
            "git format-patch --keep-subject "
            "--stdout %(remote)s/%(target)s..%(remote)s/%(init)s "
            "-- %(module)s | git am -3 --keep" % {
                'remote': remote_name,
                'init': init_version,
                'target': target_version,
                'module': module_name,
            }
        )

    def _load_migration_script(self, full_name):
        module = importlib.import_module(full_name)
        result = [x[1]()
                  for x in inspect.getmembers(module, inspect.isclass)
                  if x[0] != 'BaseMigrationScript'
                  and issubclass(x[1], BaseMigrationScript)]
        return result

    def _get_migration_scripts(self):
        # Add the script that will be allways executed
        self._migration_scripts.extend(
            self._load_migration_script(
                "odoo_module_migrate.migration_scripts.migrate_allways"
            )
        )
        if self._remove_migration_folder:
            self._migration_scripts.extend(
                self._load_migration_script(
                    "odoo_module_migrate.migration_scripts."
                    "migrate_remove_migration_folder"
                )
            )
        all_packages = importlib.\
            import_module("odoo_module_migrate.migration_scripts")

        migration_start = float(self._migration_steps[0]["init_version_code"])
        migration_end = float(self._migration_steps[-1]["target_version_code"])

        for loader, name, is_pkg in pkgutil.walk_packages(
                all_packages.__path__):
            # Ignore script that will be allways executed.
            # this script will be added at the end.
            if name in ('migrate_allways', 'migrate_remove_migration_folder'):
                continue

            # Filter migration scripts, depending of the configuration
            full_name = all_packages.__name__ + '.' + name
            if 'allways' in name:
                # replace allways by the most recent version
                real_name = name.replace("allways", _get_latest_version_code())
            else:
                real_name = name
            splitted_name = real_name.split("_")

            script_start = float(splitted_name[1])
            script_end = float(splitted_name[2])

            # Exclude scripts
            if script_start >= migration_end or script_end <= migration_start:
                continue

            self._migration_scripts.extend(
                self._load_migration_script(full_name)
            )

        logger.debug(
            "The following migration script will be"
            " executed:\n- %s" % '\n- '.join(
                [
                    inspect.getfile(x.__class__).split('/')[-1]
                    for x in self._migration_scripts]
            )
        )

    def run(self):
        logger.debug(
            "Running migration from: %s to: %s in '%s'" % (
                self._migration_steps[0]["init_version_name"],
                self._migration_steps[-1]["target_version_name"],
                self._directory_path.resolve()))
        for module_migration in self._module_migrations:
            module_migration.run()
