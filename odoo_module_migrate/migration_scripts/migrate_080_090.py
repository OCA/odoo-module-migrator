# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_module_migrate.base_migration_script import BaseMigrationScript

_TEXT_REPLACES = {
    ".py": {"select=True": "index=True"},
}

_DEPRECATED_MODULES = [
    ("account_analytic_analysis", "oca_moved", "contract", "Moved to OCA/contract"),
    (
        "account_analytic_plans",
        "oca_moved",
        "account_analytic_distribution",
        "Moved to OCA/account_analytic",
    ),
    ("account_bank_statement_extensions", "removed"),
    ("account_chart", "merged", "account"),
    ("account_check_writing", "renamed", "account_check_printing"),
    ("account_followup", "removed"),
    (
        "account_payment",
        "oca_moved",
        "account_payment_order",
        "Moved to OCA/bank-payment",
    ),
    ("account_sequence", "removed"),
    ("analytic_contract_hr_expense", "removed"),
    ("analytic_user_function", "removed"),
    ("anglo_saxon_dropshipping", "removed"),
    ("auth_openid", "removed"),
    ("base_report_designer", "removed"),
    ("contacts", "merged", "mail"),
    ("crm_helpdesk", "removed"),
    ("crm_mass_mailing", "removed"),
    ("crm_profiling", "removed"),
    ("edi", "removed"),
    ("email_template", "merged", "mail_template"),
    ("hr_applicant_document", "removed"),
    ("hr_timesheet_invoice", "removed"),
    ("im_chat", "merged", "mail"),
    ("knowledge", "oca_moved", "knowledge", "Moved to OCA/knowledge"),
    ("l10n_be_coda", "removed"),
    ("l10n_fr_rib", "removed"),
    ("marketing_crm", "merged", "crm"),
    ("multi_company", "removed"),
    ("portal_claim", "renamed", "website_crm_claim"),
    ("portal_project", "merged", "project"),
    ("portal_project_issue", "merged", "project_issue"),
    ("procurement_jit_stock", "merged", "procurement_jit"),
    (
        "purchase_analytic_plans",
        "oca_moved",
        "purchase_analytic_distribution",
        "Moved to OCA/account-analytic",
    ),
    ("purchase_double_validation", "removed"),
    (
        "sale_analytic_plans",
        "oca_moved",
        "sale_analytic_distribution",
        "Moved to OCA/account-analytic",
    ),
    ("sale_journal", "removed"),
    ("share", "removed"),
    ("stock_invoice_directly", "removed"),
    ("web_api", "removed"),
    ("web_gantt", "merged", "web"),
    ("web_graph", "merged", "web"),
    ("web_kanban_sparkline", "merged", "web"),
    ("web_tests", "merged", "web"),
    ("web_tests_demo", "removed"),
    ("website_certification", "removed"),
    ("website_instantclick", "removed"),
    ("website_mail_group", "renamed", "website_mail_channel"),
    ("website_report", "merged", "report"),
]


class MigrationScript(BaseMigrationScript):

    _TEXT_REPLACES = _TEXT_REPLACES
    _DEPRECATED_MODULES = _DEPRECATED_MODULES
