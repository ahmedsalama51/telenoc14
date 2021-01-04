# -*- coding: utf-8 -*-
{
    'name': 'Fisher Sales Modifications',
    'summary': 'New Features for product, sale module',
    'version': '1.2',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Sales',
    'depends': ['sale', 'product'],
    'website': 'http://www.telenoc.org',
    'data': [
        'views/product_view_changes.xml',
        
        'views/sale_view_changes.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
