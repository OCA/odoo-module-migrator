# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_REPLACES = {
    ".xml": {
        r"<data +noupdate=\"0\" *>": "<data>",
    }
}


def set_module_installable(**kwargs):
    tools = kwargs["tools"]
    manifest_path = kwargs["manifest_path"]
    old_term = r"('|\")installable('|\").*(False)"
    new_term = r"\1installable\2: True"
    tools._replace_in_file(
        manifest_path, {old_term: new_term}, "Set module installable"
    )


class MigrationScript(BaseMigrationScript):
    _TEXT_REPLACES = _TEXT_REPLACES
    _GLOBAL_FUNCTIONS = [
        set_module_installable,
    ]
