_FILE_RENAMES = {"__openerp__.py": "__manifest__.py"}

_TEXT_REPLACES = {
    "*": {
        "base.group_configuration": "base.group_system",
        "base.group_sale_salesman": "sales_team.group_sale_salesman",
        "base.group_sale_salesman_all_leads": "sales_team.group_sale_salesman_all_leads",
        "base.group_sale_manager": "sales_team.group_sale_manager",
    },
    ".py": {"from openerp": "from odoo", "import openerp": "import odoo"},
}
