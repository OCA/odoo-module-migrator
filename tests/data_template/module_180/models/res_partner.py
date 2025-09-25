from odoo import models, fields, api
from odoo.osv import expression
from odoo.osv.expression import AND, OR


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
    
    @api.model
    def test_groups_id_usage(self):
        # Test case 1: groups_id in domain
        records = self.search([("groups_id", "in", [1, 2, 3])])
        
        # Test case 2: groups_id in field access
        for record in records:
            if record.groups_id:
                print(record.groups_id.name)
                
        # Test case 3: groups_id in dictionary
        vals = {"groups_id": [(6, 0, [1, 2])]}
        self.create(vals)

        return records

    def search_with_expression(self, domain):
        result = expression.AND([domain, [('active', '=', True)]])
        result2 = AND([result, OR([[('is_company', '=', True)]])])
        
        return self.search(result2)
