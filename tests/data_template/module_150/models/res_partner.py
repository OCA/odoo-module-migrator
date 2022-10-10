# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def test_get_record_xml_id(self):
        return self.get_xml_id()[self.id]

    def test_loop_through_fields(self):
        group_fields = [f for f in self.fields_get_keys() if f.startswith("group_")]
        for group_field in group_fields:
            print(group_field)
