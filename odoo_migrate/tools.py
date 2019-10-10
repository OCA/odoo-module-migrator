# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import subprocess
from .config import _AVAILABLE_MIGRATION_STEPS
from .log import logger


def _get_available_init_version_names():
    return [x["init_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_available_target_version_names():
    return [x["target_version_name"] for x in _AVAILABLE_MIGRATION_STEPS]


def _get_latest_version_name():
    return _AVAILABLE_MIGRATION_STEPS[-1]["target_version_name"]


def _get_latest_version_code():
    return _AVAILABLE_MIGRATION_STEPS[-1]["target_version_code"]


def _execute_shell(shell_command):
    logger.debug("Execute Shell:\n%s" % (shell_command))
    return subprocess.check_output(shell_command, shell=True)
