# coding: utf-8
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def write(self, vals):
        # something
        return super(SaleOrder, self).write(vals)

    @api.cr
    def my_function(self):
        # something
        return
