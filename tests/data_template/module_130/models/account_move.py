from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    dummy_type = fields.Selection()

    @api.depends('type')
    def _compute_dummy(self):
       for move in self:
           move.dummy_type = move.type
