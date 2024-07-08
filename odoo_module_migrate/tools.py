# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
import subprocess
import re

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


def _execute_shell(shell_command, path=False, raise_error=True):
    if path:
        shell_command = "cd '%s' && %s" % (str(path.resolve()), shell_command)
    logger.debug("Execute Shell:\n%s" % (shell_command))
    if raise_error:
        return subprocess.check_output(shell_command, shell=True)
    else:
        return subprocess.run(shell_command, shell=True)


def _read_content(file_path):
    f = open(file_path, "r")
    text = f.read()
    f.close()
    return text


def _write_content(file_path, content):
    f = open(file_path, "w")
    f.write(content)
    f.close()


def _replace_in_file(file_path, replaces, log_message=False):
    current_text = _read_content(file_path)
    new_text = current_text

    for old_term, new_term in replaces.items():
        new_text = re.sub(old_term, new_term or "", new_text)

    # Write file if changed
    if new_text != current_text:
        if not log_message:
            log_message = "Changing content of file: %s" % file_path.name
        logger.info(log_message)
        _write_content(file_path, new_text)
    return new_text


def _get_manifest_dict(manifest_path):
    """
    :param module: The name of the module (sale, purchase, ...)"""
    if not manifest_path:
        return {}
    # default values for descriptor
    info = {
        "application": False,
        "author": "Odoo S.A.",
        "auto_install": False,
        "category": "Uncategorized",
        "depends": [],
        "description": "",
        "installable": True,
        "license": "LGPL-3",
        "post_load": None,
        "version": "1.0",
        "web": False,
        "sequence": 100,
        "summary": "",
        "website": "",
    }
    info.update(
        zip(
            "depends data demo test init_xml update_xml demo_xml".split(),
            iter(list, None),
        )
    )

    f = open(manifest_file, mode="rb")
    try:
        info.update(ast.literal_eval(pycompat.to_text(f.read())))
    finally:
        f.close()

    if not info.get("description"):
        readme_path = [
            opj(manifest_path, x)
            for x in README
            if os.path.isfile(opj(manifest_path, x))
        ]
        if readme_path:
            with open(readme_path[0]) as fd:
                info["description"] = fd.read()

    # auto_install is set to `False` if disabled, and a set of
    # auto_install dependencies otherwise. That way, we can set
    # auto_install: [] to always auto_install a module regardless of its
    # dependencies
    auto_install = info.get("auto_install", info.get("active", False))
    if isinstance(auto_install, collections.abc.Iterable):
        info["auto_install"] = set(auto_install)
        non_dependencies = info["auto_install"].difference(info["depends"])
        assert not non_dependencies, (
            "auto_install triggers must be dependencies, found "
            "non-dependencies [%s] for module %s"
            % (", ".join(non_dependencies), module)
        )
    elif auto_install:
        info["auto_install"] = set(info["depends"])
    else:
        info["auto_install"] = False

    return info
