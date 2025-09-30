from odoo import models
from odoo.fields import Domain


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def simple_search(self, base_domain):
        extra_domain = [('state', '=', 'sale')]
        result1 = Domain.AND([base_domain, extra_domain])
        result2 = Domain.OR([result1, [('state', '=', 'draft')]])
        return result2
