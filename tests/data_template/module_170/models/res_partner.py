from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    test_unaccent = fields.Char(string="test_unaccent", unaccent=False, default="test")
    test_unaccent_only = fields.Char(unaccent=False)
    test_unaccent_only_html = fields.Html(unaccent=False)
    test_unaccent_multiline = fields.Char(string="test_unaccent",
                                          unaccent=False,
                                          default="test")
    test_unaccent_only_multiline = fields.Text(
        unaccent=False,
    )

    def example_method(self):
        self.env.ref('module_name.tree_view').write({'view_mode': 'tree'})

    def example_method_has_group(self):
        if self.user_has_groups('base.group_user'):
            pass

        if self.user_has_groups("base.group_user"):
            pass

        if self.user_has_groups("!base.group_user"):
            pass

        if self.user_has_groups('base.group_user,base.group_manager'):
            pass

        if self.user_has_groups("base.group_user,base.group_manager,base.group"):
            pass
        
        if self.user_has_groups('base.group_user,!base.group_manager'):
            pass

        if self.user_has_groups("base.group_user,!base.group_manager,!base.group"):
            pass
