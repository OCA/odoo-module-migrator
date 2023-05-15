# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_REPLACES = {
    "*": {
        "base.group_configuration": "base.group_system",
        "base.group_sale_salesman": "sales_team.group_sale_salesman",
        "base.group_sale_salesman_all_leads": "sales_team.group_sale_salesman_all_leads",
        "base.group_sale_manager": "sales_team.group_sale_manager",
    },
}

_DEPRECATED_MODULES = [
    ("account_extra_reports", "removed"),
    ("account_full_reconcile", "removed"),
    ("account_tax_adjustments", "removed"),
    ("account_tax_exigible", "removed"),
    ("claim_from_delivery", "removed"),
    ("crm_claim", "removed"),
    ("crm_partner_assign", "removed"),
    ("im_odoo_support", "merged", "im_livechat"),
    ("mail_tip", "merged", "mail"),
    ("marketing", "merged", "marketing_campaign"),
    ("mrp_operations", "merged", "mrp"),
    ("product_uos", "removed"),
    ("product_visible_discount", "removed"),
    ("project_timesheet", "merged", "hr_timesheet"),
    ("report_webkit", "removed"),
    ("sale_layout", "merged", "sale"),
    ("sale_service", "merged", "sale_timesheet"),
    ("warning", "removed"),
    ("web_analytics", "removed"),
    ("web_tip", "removed"),
    ("web_view_editor", "removed"),
    ("website_crm_claim", "removed"),
]


class MigrationScript(BaseMigrationScript):
    _TEXT_REPLACES = _TEXT_REPLACES
    _DEPRECATED_MODULES = _DEPRECATED_MODULES
