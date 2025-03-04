from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def example_method_use_slugify(self, page_name):
        return "/" + self.env["ir.http"]._slugify(page_name, max_length=1024, path=True)
