from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    test_unaccent = fields.Char(string="test_unaccent", default="test")
    test_unaccent_only = fields.Char()
    test_unaccent_only_html = fields.Html()
    test_unaccent_multiline = fields.Char(string="test_unaccent", default="test")
    test_unaccent_only_multiline = fields.Text()

    def example_method(self):
        self.env.ref('module_name.tree_view').write({'view_mode': 'list'})

    def example_method_has_group(self):
        if self.env.user.has_group('base.group_user'):
            pass

        if self.env.user.has_group("base.group_user"):
            pass

        if self.env.user.has_groups("!base.group_user"):
            pass

        if self.env.user.has_groups('base.group_user,base.group_manager'):
            pass

        if self.env.user.has_groups("base.group_user,base.group_manager,base.group"):
            pass
        
        if self.env.user.has_groups('base.group_user,!base.group_manager'):
            pass

        if self.env.user.has_groups("base.group_user,!base.group_manager,!base.group"):
            pass
