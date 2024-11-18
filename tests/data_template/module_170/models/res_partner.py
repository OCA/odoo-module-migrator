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
        operation = 'read'
        self.env['account.move'].check_access_rights('read')
        self.env['account.move'].check_access_rights(operation='read')
        self.env['account.move'].check_access_rights(operation)
        self.env['account.move'].check_access_rights(operation=operation)

        self.env['account.move'].check_access_rule('write')
        self.env['account.move'].check_access_rule(operation='write')
        self.env['account.move'].check_access_rule(operation)
        self.env['account.move'].check_access_rule(operation=operation)

        self.env['account.move']._filter_access_rule('read')
        self.env['account.move']._filter_access_rule(operation='read')
        self.env['account.move']._filter_access_rule(operation)
        self.env['account.move']._filter_access_rule(operation=operation)

        self.env['account.move']._filter_access_rule_python('read')
        self.env['account.move']._filter_access_rule_python(operation='read')
        self.env['account.move']._filter_access_rule_python(operation)
        self.env['account.move']._filter_access_rule_python(operation=operation)

        if not self.env['account.move'].check_access_rights('read', raise_exception=False):
            pass

        if not self.env['account.move'].check_access_rights(operation='read', raise_exception=False):
            pass

        if not self.env['account.move'].check_access_rights(operation, raise_exception=False):
            pass

        if not self.env['account.move'].check_access_rights(operation=operation, raise_exception=False):
            pass

    def check_access_rights(self, operation, raise_exception=True):
        pass

    def check_access_rights(self, operation="read", raise_exception=True):
        pass
