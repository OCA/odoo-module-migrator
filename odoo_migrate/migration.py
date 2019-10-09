import pathlib
import os
from .config import _AVAILABLE_MIGRATION_STEPS
from .exception import ConfigException
from .log import logger


class Migration():

    _migration_steps = []
    _absolute_directory_path = False
    _use_black = False

    def __init__(
        self, init_version_name, target_version_name, relative_directory_path,
        force_black,
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

        # Get absolute directory path of the repository
        if not os.path.exists(relative_directory_path):
            raise ConfigException(
                "Unable to find directory: %s" % relative_directory_path)

        self._absolute_directory_path =\
            pathlib.Path(relative_directory_path).resolve(strict=True)

    def run(self):
        logger.info(">>> Absolute Directory Path ")
        # logger.debug(self._absolute_directory_path)
        # logger.debug(">>> The following Migration Steps will be executed")
        # logger.debug(self._migration_steps)
        # logger.debug(">>> Use black")
        # logger.debug(self._use_black)
