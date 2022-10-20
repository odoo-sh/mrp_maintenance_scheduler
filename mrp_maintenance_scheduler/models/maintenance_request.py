# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from datetime import datetime
from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _inherit='maintenance.request'

    maintenance_request_step_ids = fields.One2many("maintenance.request.step","maintenance_request_id")
    maintenance_operation_id = fields.Many2one('maintenance.operations',string="Maintenance Operation")
    duration = fields.Float(help="Duration in hours.",compute="_compute_duration_for_request_in_hours")
    member_ids = fields.Many2many(related='maintenance_team_id.member_ids')

    def _compute_duration_for_request_in_hours(self):
        for record in self:
            total_minutes = round(sum(record.maintenance_request_step_ids.mapped('duration')),2)
            record.duration = total_minutes / 60.0

    @api.onchange('maintenance_team_id')
    def onchange_maintenance_team_id(self):
        if self.maintenance_team_id.name in ['IT', 'Internal Maintenance', 'Outside Maintenance']:
            self.user_id = None

class MaintenanceRequeststep(models.Model):
    _name = "maintenance.request.step"
    _description = "Maintenance Request Step"

    step_id = fields.Many2one("maintenance.operations.step",string="Steps")
    duration_expected = fields.Float(related="step_id.duration_expected",string="Expected Duration")
    procedure = fields.Html(related="step_id.procedure",string="Procedure")
    duration = fields.Float(string="Real Duration",compute="_compute_duration",default = 0.0)
    maintenance_request_id = fields.Many2one("maintenance.request")
    maintenance_opr_id = fields.Many2one('maintenance.operations',related='maintenance_request_id.maintenance_operation_id',string="Maintenance Operation",invisible=True)
    maintenance_duration_ids = fields.Many2many('maitenance.request.duration',string="Maitenance Request Duration",store = True)
    state = fields.Selection([
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('pending','Pending'),
        ('done', 'Finished')], string='Status',
        default='ready', copy=False, readonly=True)
    is_user_working = fields.Boolean(string="User Working")

    def _compute_duration(self):
        for step in self:
            duration = self.env['maitenance.request.duration'].search([('maintenance_rquest_id','=',step.maintenance_request_id.id),
                                                            ('maintenance_step_id','=',step.id)]).mapped('duration')
            step.duration = round(sum(duration),2)

    def button_start(self):
        self.state = 'progress'
        self.env['maitenance.request.duration'].create({
                                                        'maintenance_rquest_id': self.maintenance_request_id.id,
                                                        'maintenance_step_id': self.id,
                                                        'date_start': datetime.now(),
                                                        'date_end': False,})
        self.is_user_working = True

    def _duration_calculation(self):
        mait_req_duration = self.env['maitenance.request.duration']
        domain = [('maintenance_step_id', '=', self.id), ('maintenance_rquest_id', '=', self.maintenance_request_id.id),('date_end', '=', False)]
        for duration in mait_req_duration.search(domain):
            duration.write({'date_end': fields.Datetime.now()})

    def button_stop(self):
        self.state = 'done'
        self._duration_calculation()
        self.is_user_working = False


    def button_pending(self):
        self.state = 'pending'
        self._duration_calculation()
        self.is_user_working = False

class MaintenanceRequestDuration(models.Model):
    _name = "maitenance.request.duration"
    _description = "Maitenance Request Duration"

    maintenance_rquest_id = fields.Many2one("maintenance.request",string="Maintenance Request")
    maintenance_step_id = fields.Many2one("maintenance.request.step",string="Maintenance Request Step")
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')
    duration = fields.Float('Duration',compute="_compute_request_duration",store=True)

    @api.depends('date_start','date_end')
    def _compute_request_duration(self):
        for due_time in self:
            if due_time.date_start and due_time.date_end:
                d1 = fields.Datetime.from_string(due_time.date_start)
                d2 = fields.Datetime.from_string(due_time.date_end)
                diff = d2 - d1
                if diff:
                    due_time.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                due_time.duration = 0.0
