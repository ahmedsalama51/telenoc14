# -*- coding: utf-8 -*-
{
    'name': 'E-Outlet Product Changes',
    'summary': 'New Features for product module',
    'version': '1.2',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Sales',
    'depends': ['product'],
    'website': 'http://www.telenoc.org',
    'data': [
        # 'data/product_data.xml',
        
        # 'security/',
        'security/ir.model.access.csv',

        'views/product_view_changes.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
