# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_ERRORS = {
    "*": {
        "web_settings_dashboard":
        "[V13] Reference to 'web_settings_dashboard'"
        ". This module has been removed."
    },
    ".py": {
        r".*@api.returns.*\n":
        "[13] Use of deprecated decorator '@api.returns'",
        r".*@api.cr.*\n":
        "[13] Use of deprecated decorator '@api.cr'",
        r".*@api.model_cr.*\n":
        "[13] Use of deprecated decorator '@api.model_cr'",
    },
}

_TEXT_REPLACES = {
    ".py": {
        r".*@api.one.*\n": "",
        r"\.sudo\((?P<user>[^/)]+?)\)": r".with_user(\g<user>)",
        r"\.suspend_security": ".sudo",
        r"\"base_suspend_security\",\n": "",
        r"\._find_partner_from_emails\(": "._mail_find_partner_from_emails(",
        r"\._search_on_partner\(": "._mail_search_on_partner(",
        r"\._search_on_user\(": "._mail_search_on_user(",
    },
    ".xml": {
        r"( |\t)*<field name=('|\")view_type('|\")>.*</field>\n": "",
        r"src_model": "binding_model",
    }
}


class MigrationScript(BaseMigrationScript):
    _TEXT_ERRORS = _TEXT_ERRORS
    _TEXT_REPLACES = _TEXT_REPLACES
