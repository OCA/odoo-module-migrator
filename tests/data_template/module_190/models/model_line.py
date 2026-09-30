from odoo import fields, models


class TestModelLine(models.Model):
    _name = "test.model_line"
    _description = "Test line"

    name = fields.Char()

    def _get_batch_size(self):
        return int(self.env["ir.config_parameter"].sudo().get_param("module.batch_size", 20))
