# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import subprocess

_TEXT_REPLACES = {
    ".xml": {
        r"<data +noupdate=\"0\" *>": "<data>",
    }
}


def bump_revision(**kwargs):
    tools = kwargs['tools']
    manifest_path = kwargs['manifest_path']
    target_version_name = kwargs['migration_steps'][-1]["target_version_name"]

    new_version = "%s.1.0.0" % target_version_name

    old_term = r"('|\")version('|\").*('|\").*('|\")"
    new_term = r'\1version\2: "{0}"'.format(new_version)
    tools._replace_in_file(
        manifest_path, {old_term: new_term},
        "Bump version to %s" % new_version)


def set_module_installable(**kwargs):
    tools = kwargs['tools']
    manifest_path = kwargs['manifest_path']
    old_term = r"('|\")installable('|\").*(False)"
    new_term = r"\1installable\2: True"
    tools._replace_in_file(
        manifest_path, {old_term: new_term}, "Set module installable")


def remove_migration_folder(**kwargs):
    logger = kwargs['logger']
    module_path = kwargs['module_path']
    migration_path_folder = os.path.join(module_path, 'migrations')
    if os.path.exists(migration_path_folder):
        logger.info("Removing 'migrations' folder")
        subprocess.check_output("rm -r %s" % migration_path_folder, shell=True)


_GLOBAL_FUNCTIONS = [
    remove_migration_folder, set_module_installable, bump_revision]
