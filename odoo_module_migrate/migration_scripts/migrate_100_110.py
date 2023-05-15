# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

# TODO: Call 2to3

_TEXT_REPLACES = {
    "*": {
        r"ir.actions.report.xml": "ir.actions.report",
        r"report.external_layout": "web.external_layout",
        r"report.html_container": "web.html_container",
        r"report.layout": "web.report_layout",
        r"report.minimal_layout": "web.minimal_layout",
    },
    ".xml": {
        r"kanban_state_selection": "state_selection",
    },
}

_TEXT_ERRORS = {
    "*": {
        "('|\")workflow('|\")": "[V11] Reference to 'workflow'."
        " This model has been removed.",
        "('|\")workflow.activity('|\")": "[V11] Reference to 'workflow.activity'."
        " This model has been removed.",
        "('|\")workflow.instance('|\")": "[V11] Reference to'workflow.instance'."
        " This model has been removed.",
        "('|\")workflow.transition('|\")": "[V11] Reference to 'workflow.transition'."
        " This model has been removed.",
        "('|\")workflow.triggers('|\")": "[V11] Reference to 'workflow.triggers'."
        " This model has been removed.",
        "('|\")workflow.workitem('|\")": "[V11] Reference to 'workflow.workitem'."
        " This model has been removed.",
        "report.external_layout_header": "report.external_layout_header is obsolete.",
        "report.external_layout_footer": "report.external_layout_footer is obsolete.",
    },
    ".xml": {
        r"<tree[\s][^>]*colors=": "colors attribute is deprecated in tree view."
        " Use decoration- instead.",
        r"<tree[\s][^>]*fonts=": "fonts attribute is deprecated in tree view."
        " Use decoration- instead.",
    },
}

_DEPRECATED_MODULES = [
    ("account_accountant", "removed"),
    ("account_tax_cash_basis", "removed"),
    ("base_action_rule", "renamed", "base_automation"),
    ("crm_project_issue", "renamed", "crm_project_issue"),
    (
        "hr_timesheet_sheet",
        "oca_moved",
        "hr_timesheet_sheet",
        "Moved to OCA/hr-timesheet",
    ),
    ("marketing_campaign", "removed"),
    ("marketing_campaign_crm_demo", "removed"),
    ("portal_gamification", "merged", "gamification"),
    ("portal_sale", "merged", "sale"),
    ("portal_stock", "merged", "portal"),
    ("procurement", "merged", "stock"),
    ("project_issue", "merged", "project"),
    ("project_issue_sheet", "merged", "hr_timesheet"),
    ("rating_project_issue", "removed"),
    ("report", "merged", "base"),
    ("stock_calendar", "removed"),
    ("stock_picking_wave", "renamed", "stock_picking_batch"),
    ("subscription", "removed"),
    ("web_calendar", "merged", "web"),
    ("web_kanban", "merged", "web"),
    ("website_issue", "renamed", "website_form_project"),
    ("website_portal", "merged", "website"),
    ("website_project", "merged", "project"),
    ("website_project_issue", "merged", "project"),
    ("website_project_timesheet", "merged", "hr_timesheet"),
    ("website_rating_project_issue", "renamed", "website_rating_project"),
]


class MigrationScript(BaseMigrationScript):

    _TEXT_REPLACES = _TEXT_REPLACES
    _TEXT_ERRORS = _TEXT_ERRORS
    _DEPRECATED_MODULES = _DEPRECATED_MODULES
