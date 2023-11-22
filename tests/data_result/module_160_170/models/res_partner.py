from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field_1 = fields.Boolean()
    task_ids = fields.One2many('project.task')
    task_count = fields.Integer(compute='_compute_task_count', string='# Tasks')

    def _compute_task_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)],
            ['parent_id'],
        )
        task_data = self.env['project.task']._read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            groupby=['partner_id'], aggregates=['__count']
        )
        group_dependent = self.env['project.task']._read_group([
            ('depend_on_ids', 'in', task_data.ids),
            ], ['depend_on_ids'], ['__count'])
