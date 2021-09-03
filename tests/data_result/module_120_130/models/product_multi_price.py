from odoo import fields, models, api


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
        digits='Product Price',
    )

    def _some_method(self):
        return self.env.user.company_id
