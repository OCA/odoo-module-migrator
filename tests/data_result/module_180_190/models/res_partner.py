from odoo import models, fields, api
from odoo.fields import Domain


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
    
    @api.model
    def test_groups_id_usage(self):
        # Test case 1: groups_id in domain
        records = self.search([("group_ids", "in", [1, 2, 3])])
        
        # Test case 2: groups_id in field access
        for record in records:
            if record.group_ids:
                print(record.group_ids.name)
                
        # Test case 3: groups_id in dictionary
        vals = {"group_ids": [(6, 0, [1, 2])]}
        self.create(vals)

        return records

    def search_with_expression(self, domain):
        result = Domain.AND([domain, [('active', '=', True)]])
        result2 = Domain.AND([result, Domain.OR([[('is_company', '=', True)]])])
        
        return self.search(result2)
