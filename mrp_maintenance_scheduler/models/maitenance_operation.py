# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class MaintenanceOperations(models.Model):
    _name = "maintenance.operations"
    _description = "Maintenance Operations"
    
    name = fields.Char(string="Name")
    line_ids = fields.One2many("maintenance.operations.step","operation_id",string="Steps")
    
    
    
class MaintenanceOperationsLine(models.Model):
    _name = "maintenance.operations.step"
    _description = "Maintenance Operations Step"
    _rec_name = "step_name"
    
    step_name = fields.Char(string="Step Name")
    duration_expected = fields.Float(string="Expected Duration")
    procedure = fields.Html("Procedure")
    operation_id = fields.Many2one("maintenance.operations")