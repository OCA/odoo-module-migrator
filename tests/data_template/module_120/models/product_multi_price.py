from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
import odoo.addons.decimal_precision


class ProductMultiPrice(models.Model):
    _name = 'product.multi.price'
    _description = "Product Multiple Prices"

    name = fields.Many2one(
        comodel_name='product.multi.price.name',
        required=True,
        translate=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        ondelete='cascade',
    )
    price = fields.Float(
        digits=dp.get_precision('Product Price'),
    )

    @api.one
    @api.multi
    def _some_method(self):
        return self.env.user.company_id
