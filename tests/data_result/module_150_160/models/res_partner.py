# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    def test_get_record_xml_id(self):
        return self.get_external_id()[self.id]

    def test_loop_through_fields(self):
        group_fields = [f for f in self._fields if f.startswith("group_")]
        for group_field in group_fields:
            print(group_field)

    def test_removed_field(self):
        return self.env['product.product'].search([], limit=1).price

    def test_renamed_field(self):
        return self.env['account.account'].search([], limit=1).user_type_id

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        self.flush()
        self.invalidate_cache(['user_ids'], self._ids)
        args = args or []
        if name:
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
