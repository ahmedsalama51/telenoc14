# -*- coding: utf-8 -*-
{
    'name': 'Telenoc Stock Return',
    'summary': 'New Features for ',
    'version': '0.1',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Operations/Inventory',
    'depends': ['stock'],
    'website': 'http://www.telenoc.org',
    'data': [
        'data/stock_return_data.xml',
    
        'security/hr_supervisor_attendance_security.xml',
        'security/ir.model.access.csv',
    
        'views/stock_location_view_changes.xml',
        'views/stock_return_view.xml',
        'views/stock_picking_view_changes.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
