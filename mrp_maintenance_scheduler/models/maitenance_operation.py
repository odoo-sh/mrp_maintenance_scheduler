# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class MaintenanceOperations(models.Model):
    _name = "maintenance.operations"
    _description = "Maintenance Operations"
    _inherit = ['mail.thread']
    
    name = fields.Char(string="Name")
    period = fields.Integer(string='Preventive Maintenance Frequency')
    maintenance_duration = fields.Float(help="Maintenance Duration in hours.")
    technician_user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team',required=True)
    line_ids = fields.One2many("maintenance.operations.step","operation_id",string="Steps")

    @api.onchange('maintenance_team_id')
    def onchange_maintenance_team_id(self):
        if self.maintenance_team_id.name in ['IT', 'Internal Maintenance']:
            return {'domain': {'technician_user_id': [('share', '=', False)]}}
        return {'domain': {'technician_user_id': [('id', 'in', self.env['res.users'].search([]).ids)]}}

class MaintenanceOperationsLine(models.Model):
    _name = "maintenance.operations.step"
    _description = "Maintenance Operations Step"
    _rec_name = "step_name"

    step_name = fields.Char(string="Step Name")
    duration_expected = fields.Float(string="Expected Duration",required=True)
    procedure = fields.Html("Procedure")
    operation_id = fields.Many2one("maintenance.operations")