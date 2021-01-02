# -*- coding: utf-8 -*-
{
    'name': "Hr Administrative Decisions",
    'summary': """
        Hr Administrative Decisions""",
    'description': """
        Hr Administrative Decisions
    """,
    'author': "Magdy, Ahmed Salama ,Helcon",
    'website': "https://telenoc.org",
    'category': 'Human Resources',
    'version': '0.3',
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'data/administrative_decisions_data.xml',
        
        'security/ir.model.access.csv',
        
        'views/administrative_decisions_view.xml',
        'views/hr_employee.xml',
        
        'report/administrative_decision.xml',
    ],
}
