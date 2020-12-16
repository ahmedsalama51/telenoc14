# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Request Template',
    'summary': 'Add some types of templates for employee requests',
    'version': '0.1',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Human Resources/Employee',
    'depends': ['hr'],
    'website': 'http://www.telenoc.org',
    'data': [
        'data/hr_employee_request_data.xml',
        'data/hr_employee_request_type_data.xml',
        
        # 'security/',
        'security/ir.model.access.csv',

        'views/hr_employee_request_type_view.xml',
        'views/hr_employee_request_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
