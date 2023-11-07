from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
