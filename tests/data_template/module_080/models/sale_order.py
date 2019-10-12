# coding: utf-8
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
