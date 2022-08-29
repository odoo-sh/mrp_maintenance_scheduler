# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Mrp Maintenance Scheduler",
    "summary": """ This module is used to schedule the maintenance""",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "http://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "depends": [
        'base',
        'maintenance',
        'mrp',
    ],
    "data": [
        'data/maintenance_cron.xml',
        'security/ir.model.access.csv',
        'views/maitenance_operation.xml',
        'views/res_config_settings.xml',
        'views/maintenance_equipment.xml',
        'views/maintenance_request.xml',
        'views/assets.xml',
    ],
}
