from odoo import models, fields


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

    test_1 = fields.Char(required=True)
