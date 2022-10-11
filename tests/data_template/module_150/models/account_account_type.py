from odoo import fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    analytic_account_required = fields.Boolean(
        string='Analytic Account Required?',
        help="If True, then an analytic account will be required when posting "
        "journal entries with this type of account.",
    )
    analytic_tag_required = fields.Boolean(
        string='Analytic Tag Required?',
        help="If True, then analytic tags will be required when posting "
        "journal entries with this type of account.",
    )
