from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()

    def example_method(self):
        self.env.ref('module_name.tree_view').write({'view_mode': 'tree'})
