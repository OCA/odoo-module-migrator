# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_field = fields.Char(string="My Custom Field")

    def write(self, vals):
        # something
        return super(SaleOrder, self).write(vals)

    @api.cr
    def my_function(self):
        # 13.0 preserve sudo
        sudo_test = self.sudo()
        self.sudo().test()

        # 13.0 should replace with with_user
        sudo_test = self.with_user(self.env.user)
        self.with_user(self.env.user).test()

        # 13.0 should replace with sudo()
        suspended = self.sudo()
        self.sudo().write({"name": "name"})
        return
