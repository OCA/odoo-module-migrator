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
    
    def example_method_access(self):
        self.env['account.move'].check_access_rights('read')
        self.env['account.move'].check_access_rule('write')
        self.env['account.move']._filter_access_rule('read')
        self.env['account.move']._filter_access_rule_python('read')
        
        if not self.env['account.move'].check_access_rights('read', raise_exception=False):
            pass
