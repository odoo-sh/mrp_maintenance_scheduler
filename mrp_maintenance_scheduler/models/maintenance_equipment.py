# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api
from datetime import timedelta

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    maintenance_equipment_step_ids = fields.One2many("maintenance.equipment.step","maintenance_equipment_id",string="Maintenance Operation")
    
    
class MaintenanceEquipmentStep(models.Model):
    _name = "maintenance.equipment.step"
    _description = "Maintenance Equipment Step"
    
    maintenance_equipment_id = fields.Many2one("maintenance.equipment")
    maintenance_operation_id = fields.Many2one('maintenance.operations',string="Maintenance Operation")
    technician_user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team',required=True)
    maintenance_duration = fields.Float(help="Maintenance Duration in hours.")
    next_action_date = fields.Date(compute='_compute_next_maintenance',store=True,string='Next Preventive Maintenance')
    period = fields.Integer(string='Preventive Maintenance Frequency')
    
    
    
    @api.depends('maintenance_equipment_id.effective_date', 'period', 'maintenance_equipment_id.maintenance_ids.request_date', 'maintenance_equipment_id.maintenance_ids.close_date')
    def _compute_next_maintenance(self):
        date_now = fields.Date.context_today(self)
        equipments = self.filtered(lambda x: x.period > 0)
        for equipment in equipments:
            next_maintenance_todo = self.env['maintenance.request'].search([
                ('equipment_id', '=', equipment.maintenance_equipment_id.id),
                ('maintenance_type', '=', 'preventive'),
                ('stage_id.done', '!=', True),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_maintenance_done = self.env['maintenance.request'].search([
                ('equipment_id', '=', equipment.maintenance_equipment_id.id),
                ('maintenance_type', '=', 'preventive'),
                ('stage_id.done', '=', True),
                ('close_date', '!=', False)], order="close_date desc", limit=1)
            if next_maintenance_todo and last_maintenance_done:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - last_maintenance_done.close_date
                # If the gap between the last_maintenance_done and the next_maintenance_todo one is bigger than 2 times the period and next request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2 and next_maintenance_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_maintenance_done.close_date + timedelta(days=equipment.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_maintenance_done.close_date + timedelta(days=equipment.period)
            elif next_maintenance_todo:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - date_now
                # If next maintenance to do is in the future, and in more than 2 times the period, we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2:
                    next_date = date_now + timedelta(days=equipment.period)
            elif last_maintenance_done:
                next_date = last_maintenance_done.close_date + timedelta(days=equipment.period)
                # If when we add the period to the last maintenance done and we still in past, we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = equipment.maintenance_equipment_id.effective_date + timedelta(days=equipment.period)
            equipment.next_action_date = next_date
        (self - equipments).next_action_date = False
    
    
    