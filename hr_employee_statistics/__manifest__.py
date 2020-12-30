# -*- coding: utf-8 -*-
{
    'name': 'Employee Statistics',
    'summary': 'New object for Employee Statistics',
    'version': '0.1',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Human Resources/Employee',
    'depends': ['hr_administrative_decisions', 'hr_supervisor_attendance'],
    'website': 'http://www.telenoc.org',
    'data': [
        'security/ir.model.access.csv',
        
        'data/hr_employee_statistics_data.xml',
        
        'views/hr_employee_statistics_view.xml',
        
        'wizard/hr_employee_statistics_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
