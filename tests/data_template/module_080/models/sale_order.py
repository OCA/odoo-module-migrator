# coding: utf-8
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_field = fields.Char(string="My Custom Field")

    @api.multi
    def write(self, vals):
        # something
        return super(SaleOrder, self).write(vals)

    @api.cr
    def my_function(self):
        # 13.0 preserve sudo
        sudo_test = self.sudo()
        self.sudo().test()

        # 13.0 should replace with with_user
        sudo_test = self.sudo(self.env.user)
        self.sudo(self.env.user).test()

        # 13.0 should replace with sudo()
        suspended = self.suspend_security()
        self.suspend_security().write({"name": "name"})

        # 13.0 should replace with new method names
        partner_ids = self._find_partner_from_emails(["Mr Test <test@example.com>"])
        partner_ids = self._search_on_partner(["test@example.com"])
        partner_ids = self._search_on_user(["test@example.com"])
        return
