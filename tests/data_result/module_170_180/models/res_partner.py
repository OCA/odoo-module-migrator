from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()

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
    
    def example_method_access(self):
        operation = 'read'
        self.env['account.move'].check_access('read')
        self.env['account.move'].check_access('read')
        self.env['account.move'].check_access(operation)
        self.env['account.move'].check_access(operation)

        self.env['account.move'].check_access('write')
        self.env['account.move'].check_access('write')
        self.env['account.move'].check_access(operation)
        self.env['account.move'].check_access(operation)

        self.env['account.move']._filter_access('read')
        self.env['account.move']._filter_access('read')
        self.env['account.move']._filter_access(operation)
        self.env['account.move']._filter_access(operation)

        self.env['account.move']._filter_access('read')
        self.env['account.move']._filter_access('read')
        self.env['account.move']._filter_access(operation)
        self.env['account.move']._filter_access(operation)

        if not self.env['account.move'].has_access('read'):
            pass

        if not self.env['account.move'].has_access('read'):
            pass

        if not self.env['account.move'].has_access(operation):
            pass

        if not self.env['account.move'].has_access(operation):
            pass

        self.env["res.brand"].has_access('read')
        self.env["res.brand"].check_access('read')

        self.env["res.brand"].has_access('write')

        self.env["res.brand"].check_access('read')

    def check_access(self, operation: str) -> None:
        pass

    def check_access(self, operation: str = 'read') -> None:
        pass

    def filter_access(self, operation: str) -> None:
        pass

    def filter_access(self, operation: str = 'read') -> None:
        pass

    def filter_access(self, operation: str) -> None:
        pass

    def filter_access(self, operation: str = 'read') -> None:
        pass
