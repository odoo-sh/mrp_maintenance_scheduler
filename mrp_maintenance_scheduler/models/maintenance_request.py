# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _inherit='maintenance.request'
    
    maintenance_request_step_ids = fields.One2many("maintenance.request.step","maintenance_request_id")
    maintenance_operation_id = fields.Many2one('maintenance.operations',string="Maintenance Operation")
    
    
class MaintenanceRequeststep(models.Model):
    _name = "maintenance.request.step"
    _description = "Maintenance Request Step"
    
    
    
    steps_id = fields.Many2one("maintenance.operations.step",string="Steps")
    duration_excpected = fields.Float(related="steps_id.duration_expected",string="Expected Duration")
    real_duration = fields.Float(string="Real Duration")
    maintenance_request_id = fields.Many2one("maintenance.request")
    maintenance_opr_id = fields.Many2one('maintenance.operations',related='maintenance_request_id.maintenance_operation_id',string="Maintenance Operation",invisible=True)
    
    
    def button_start(self):
        return
    
    def button_stop(self):
        return