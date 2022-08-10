# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'
    
    mrp_maintenance_scheduler = fields.Boolean(string="Maintenance Scheduler",config_parameter='mrp_maintenance_scheduler.mrp_maintenance_scheduler',help="Allows multiple maintenance schedule for a equipment.")