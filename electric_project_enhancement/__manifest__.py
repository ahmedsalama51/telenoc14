# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    'name': "Telenoc Electric Project Enhancement",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Project',
    'summary': """Product Card Report""",
    'website': 'http://www.telenoc.org',
    'license': 'AGPL-3',
    'description': """
    This module add new new futures and models
""",
    'version': '.1',
    'depends': ['project', 'sale_stock', 'hr'],
    'data': [
        'data/receive_cabel_rule_data.xml',
        
        'security/ir.model.access.csv',
        
        'reports/report_stock_picking_operation_changes.xml',
        'reports/report_stock_picking_delivery_slip_changes.xml',
        
        'views/project_task_view_changes.xml',
        'views/stock_picking_view_changes.xml',
        'views/receive_cable_rule_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
