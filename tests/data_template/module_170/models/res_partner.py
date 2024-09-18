from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()

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
