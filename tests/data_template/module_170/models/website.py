from odoo import api, models
from odoo.addons.http_routing.models.ir_http import slugify


class Website(models.Model):
    _inherit = "website"

    @api.model
    def example_method_use_slugify(self, page_name):
        return "/" + slugify(page_name, max_length=1024, path=True)
