from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    test_field_2 = fields.Char()

    _name_uniq = models.Constraint(
        'unique(test_field_2)',
        "The name must be unique!",
    )
    _email_check = models.Constraint(
        "CHECK(test_field_2 LIKE '%@%')",
        "Invalid email format",
    )
    _phone_not_empty = models.Constraint('CHECK(test_field_2 IS NOT NULL OR test_field_2 IS NOT NULL)')
    _long_constraint_example = models.Constraint(
        'CHECK(LENGTH(test_field_2) > 2 AND LENGTH(test_field_2) < 100 AND test_field_2 IS NOT NULL)',
        "Name validation",
    )
