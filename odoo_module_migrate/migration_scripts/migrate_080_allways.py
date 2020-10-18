# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_FILE_RENAMES = {"__openerp__.py": "__manifest__.py"}

_TEXT_REPLACES = {
    ".py": {"from openerp": "from odoo", "import openerp": "import odoo"},
    ".xml": {
        r"( |\t)*<openerp>": "<odoo>",
        r"( |\t)*<\/openerp>": "</odoo>",
    }
}
