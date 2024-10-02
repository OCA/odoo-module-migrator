# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_FILE_RENAMES = {"__openerp__.py": "__manifest__.py"}

_TEXT_ERRORS = {
    ".xml": {
        r'<xpath\s+expr="[^"]*\[@string=': "Error: The '@string=' xpath expression is deprecated.",
    }
}
_TEXT_REPLACES = {
    ".py": {"from openerp": "from odoo", "import openerp": "import odoo"},
    ".xml": {
        r"( |\t)*<openerp>(\n| |\t)*<data>": "<odoo>",
        r"( |\t)*<\/data>(\n| |\t)*<\/openerp>": "</odoo>",
    },
}


class MigrationScript(BaseMigrationScript):

    _FILE_RENAMES = _FILE_RENAMES
    _TEXT_REPLACES = _TEXT_REPLACES
    _TEXT_ERRORS = _TEXT_ERRORS
