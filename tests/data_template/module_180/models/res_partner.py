from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    test_field_2 = fields.Char()

    _sql_constraints = [
        ("name_uniq", "unique(test_field_2)", "The name must be unique!"),
        ("email_check", "CHECK(test_field_2 LIKE '%@%')", "Invalid email format"),
        ("phone_not_empty", "CHECK(test_field_2 IS NOT NULL OR test_field_2 IS NOT NULL)"),
        ("long_constraint_example", "CHECK(LENGTH(test_field_2) > 2 AND LENGTH(test_field_2) < 100 AND test_field_2 IS NOT NULL)", "Name validation"),
    ]
