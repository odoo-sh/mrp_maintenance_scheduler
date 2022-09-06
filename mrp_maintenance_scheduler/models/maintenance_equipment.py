# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api, _
from datetime import timedelta

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    maintenance_equipment_scheduler_ids = fields.One2many("maintenance.equipment.scheduler","maintenance_equipment_id",string="Maintenance Operation")

    def _prepare_maintenance_request_vals(self, date):
        res = super(MaintenanceEquipment, self)._prepare_maintenance_request_vals(date)
        mt_operation_id = self._context.get('mt_operation_id',False)
        if mt_operation_id:
            maintenance_operation_id = self.env['maintenance.operations'].browse(mt_operation_id)
            step_line_vals = []
            for rec in maintenance_operation_id.line_ids:
                step_line_vals.append([0,0,{
                                        'step_id':  rec.id,
                                        }])
            res.update({
                'maintenance_operation_id': maintenance_operation_id.id,
                'maintenance_request_step_ids': step_line_vals,
                'user_id': maintenance_operation_id.technician_user_id.id,
                'maintenance_team_id': maintenance_operation_id.maintenance_team_id.id,
            })
        return res

    @api.model
    def _cron_generate_multi_requests(self):
        mt_eq_scheduler_ids = self.env['maintenance.equipment.scheduler'].search([('maintenance_operation_id.period','>',0)])
        for mt_eq_scheduler_id in mt_eq_scheduler_ids:
            next_requests = self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', mt_eq_scheduler_id.maintenance_equipment_id.id),
                                                    ('maintenance_operation_id', '=' , mt_eq_scheduler_id.maintenance_operation_id.id),
                                                    ('maintenance_type', '=', 'preventive'),
                                                    ('request_date', '=', mt_eq_scheduler_id.next_action_date)])
            if not next_requests:
                mt_eq_scheduler_id.maintenance_equipment_id.with_context(mt_operation_id=mt_eq_scheduler_id.maintenance_operation_id.id)._create_new_request(mt_eq_scheduler_id.next_action_date)

    
    
class MaintenanceEquipmentScheduler(models.Model):
    _name = "maintenance.equipment.scheduler"
    _description = "Maintenance Equipment Scheduler"
    
    maintenance_equipment_id = fields.Many2one("maintenance.equipment")
    maintenance_operation_id = fields.Many2one('maintenance.operations',string="Maintenance Operation")
    next_action_date = fields.Date(compute='_compute_next_maintenance',store=True,string='Next Preventive Maintenance(Days)',readonly=False)

    @api.depends('maintenance_equipment_id.effective_date', 'maintenance_operation_id.period', 'maintenance_equipment_id.maintenance_ids.request_date', 'maintenance_equipment_id.maintenance_ids.close_date')
    def _compute_next_maintenance(self):
        date_now = fields.Date.context_today(self)
        mt_eq_scheduler_ids = self.filtered(lambda x: x.maintenance_operation_id.period > 0)
        for mt_eq_scheduler_id in mt_eq_scheduler_ids:
            next_maintenance_todo = self.env['maintenance.request'].search([
                ('equipment_id', '=', mt_eq_scheduler_id.maintenance_equipment_id.id),
                ('maintenance_operation_id', '=' , mt_eq_scheduler_id.maintenance_operation_id.id),
                ('maintenance_type', '=', 'preventive'),
                ('stage_id.done', '!=', True),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_maintenance_done = self.env['maintenance.request'].search([
                ('equipment_id', '=', mt_eq_scheduler_id.maintenance_equipment_id.id),
                ('maintenance_operation_id', '=' , mt_eq_scheduler_id.maintenance_operation_id.id),
                ('maintenance_type', '=', 'preventive'),
                ('stage_id.done', '=', True),
                ('close_date', '!=', False)], order="close_date desc", limit=1)
            if next_maintenance_todo and last_maintenance_done:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - last_maintenance_done.close_date
                # If the gap between the last_maintenance_done and the next_maintenance_todo one is bigger than 2 times the period and next request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period) * 2 and next_maintenance_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_maintenance_done.close_date + timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_maintenance_done.close_date + timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period)
            elif next_maintenance_todo:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - date_now
                # If next maintenance to do is in the future, and in more than 2 times the period, we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period) * 2:
                    next_date = date_now + timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period)
            elif last_maintenance_done:
                next_date = last_maintenance_done.close_date + timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period)
                # If when we add the period to the last maintenance done and we still in past, we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = fields.Datetime.today() + timedelta(days=mt_eq_scheduler_id.maintenance_operation_id.period)
            mt_eq_scheduler_id.next_action_date = next_date
        (self - mt_eq_scheduler_ids).next_action_date = False
    
    
    