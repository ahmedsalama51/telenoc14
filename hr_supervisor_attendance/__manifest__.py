# -*- coding: utf-8 -*-
{
    'name': 'HR Supervisor Attendance',
    'summary': 'New Features for HR supervisor attendance',
    'version': '0.4',
    'license': "AGPL-3",
    'author': 'Telenoc, Ahmed Salama',
    'category': 'Human Resources/Attendances',
    'depends': ['hr', 'hr_attendance'],
    'website': 'http://www.telenoc.org',
    'data': [
        'data/hr_supervisor_attendance_data.xml',
        'security/hr_supervisor_attendance_security.xml',
        'security/ir.model.access.csv',

        'views/hr_supervisor_attendance_view.xml',
        'views/hr_employee_view_changes.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
