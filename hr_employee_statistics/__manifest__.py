# -*- coding: utf-8 -*-
{
    'name': 'Employee Statistics',
    'summary': 'New object for Employee Statistics',
    'version': '1.3',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Human Resources/Employee',
    'depends': ['hr_administrative_decisions', 'hr_supervisor_attendance'],
    'website': 'http://www.telenoc.org',
    'data': [
        'security/ir.model.access.csv',
        
        'data/hr_employee_statistics_data.xml',
        
        'views/hr_employee_statistics_view.xml',
        'views/hr_supervisor_attendance_view_changes.xml',
        'views/hr_payslip_view_changes.xml',
        
        'wizard/hr_employee_statistics_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
