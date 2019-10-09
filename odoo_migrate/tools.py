import subprocess
from .config import _AVAILABLE_MIGRATION_STEPS
from .log import logger


def _get_available_init_version_names():
    return [x["init_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_available_target_version_names():
    return [x["target_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_latest_version_name():
    return _AVAILABLE_MIGRATION_STEPS[-1]["target_version_name"]


def _execute_shell(shell):
    logger.debug("Execute Shell:\n%s" % (shell))
    return subprocess.check_output(shell, shell=True)
