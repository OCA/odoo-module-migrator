import pathlib
import os
from .config import _AVAILABLE_MIGRATION_STEPS
from .exception import ConfigException
from .log import logger
from .tools import _execute_shell


class Migration():

    _migration_steps = []
    _directory_path = False
    _use_black = False

    _module_names = []

    def __init__(
        self, relative_directory_path, init_version_name, target_version_name,
        module_names=[], format_patch=False, remote_name='origin',
        force_black=False
    ):
        pass
        # Get migration steps that will be runned
        found = False
        self._use_black = force_black
        for item in _AVAILABLE_MIGRATION_STEPS:
            if not found and item["init_version_name"] != init_version_name:
                continue
            else:
                found = True
            self._migration_steps.append(item)
            self._use_black = self._use_black or item.get("use_black", False)
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

        self._module_names = module_names

    def _is_module_path(self, module_path):
        return (module_path / "__openerp__.py").exists() or\
            (module_path / "__manifest__.py").exists()

    def _get_code_from_previous_branch(self, module_name, remote_name):
        init_version = self._migration_steps[0]["init_version_name"]
        target_version = self._migration_steps[-1]["target_version_name"]
        branch_name = "%(version)s-mig-%(module_name)s" % {
            'version': target_version,
            'module_name': module_name}

        logger.info("Creating new branch '%s' ..." % (branch_name))
        _execute_shell(
            "cd %(path)s && "
            "git checkout -b %(branch)s %(remote)s/%(version)s" % {
                'path': self._directory_path.resolve(),
                'branch': branch_name,
                'remote': remote_name,
                'version': target_version,
            })

        _execute_shell(
            "cd %(path)s && "
            "git format-patch --keep-subject "
            "--stdout %(remote)s/%(target)s..%(remote)s/%(init)s "
            "-- %(module)s | git am -3 --keep" % {
                'path': self._directory_path.resolve(),
                'remote': remote_name,
                'init': init_version,
                'target': target_version,
                'module': module_name,
            }
        )

    def run(self):
        logger.info(
            "Running migration from %s to %s:\n"
            "- Directory: %s\n"
            "- Modules: %s" % (
                self._migration_steps[0]["init_version_name"],
                self._migration_steps[-1]["target_version_name"],
                self._directory_path.resolve(),
                self._module_names))
