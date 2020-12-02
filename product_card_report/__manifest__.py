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
    'name': "Product Card Report",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Inventory',
    'summary': """Product Card Report""",
    'website': 'http://www.telenoc.org',
    'license': 'AGPL-3',
    'description': """
    This module add new report Product Card added to inventory reports
""",
    'version': '.3',
    'depends': ['stock', 'sale', 'sale_stock'],
    'data': [
        'data/report_paperformat.xml',
        'data/product_card_wizard_states.xml',
        'data/stock_move_line_data.xml',
    
        'security/ir.model.access.csv',
    
        'wizard/product_card_report_wizard_view.xml',
    
        'report/product_card_report_view.xml',
    
        'views/res_config_settings_view_changes.xml',
        'views/product_card_report_doc.xml',
        'views/stock_move_view_change.xml',
        'views/stock_picking_view_changes.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
