from odoo import models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def simple_search(self, base_domain):
        extra_domain = [('state', '=', 'sale')]
        result1 = expression.AND([base_domain, extra_domain])
        result2 = expression.OR([result1, [('state', '=', 'draft')]])
        return result2
