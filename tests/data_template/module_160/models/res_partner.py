from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    task_ids = fields.One2many('project.task')
    task_count = fields.Integer(compute='_compute_task_count', string='# Tasks')
    last_name = fields.Char()

    def _compute_task_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)],
            ['parent_id'],
        )
        task_data = self.env['project.task']._read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        group_dependent = self.env['project.task']._read_group([
            ('depend_on_ids', 'in', task_data.ids),
            ], ['depend_on_ids'], ['depend_on_ids'])

    def name_get(self):
        result = []
        if self.test_field_1:
            return super().name_get()
        for partner in self:
            name = partner.name + ' ' + partner.last_name
            result.append((partner.id, name))
        return result
