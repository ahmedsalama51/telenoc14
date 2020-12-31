# -*- coding: utf-8 -*-
from odoo import models, fields, api
import calendar
import datetime
YEAR = 2000  # replace 2000 with your a start year
YEAR_LIST = []
while YEAR != 2030:  # replace 2030 with your end year
    YEAR_LIST.append((str(YEAR), str(YEAR)))
    YEAR += 1
MONTHS = [
    ('1', 'يناير'),
    ('2', 'فبراير'),
    ('3', 'مارس'),
    ('4', 'ابريل'),
    ('5', 'مايو'),
    ('6', 'يونيو'),
    ('7', 'يوليو'),
    ('8', 'اغسطس'),
    ('9', 'سبتمبر'),
    ('10', 'اكتوبر'),
    ('11', 'نوفمبر'),
    ('12', 'ديسمبر'),
]
# Ahmed Salama Code Start ---->


class ProductCardReportWizardStates(models.TransientModel):
    _name = 'hr.employee.statistics.wizard'
    _description = "HR Employee Statistics Wizard"
    _check_company_auto = True
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    date_month = fields.Selection(selection=MONTHS, string='Month', required=True
                                  , default=str(fields.Date.today().month))
    date_year = fields.Selection(YEAR_LIST, string="Year", default=str(fields.Date.today().year), required=True)
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    department_ids = fields.Many2many('hr.department', string='Department',
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    @api.onchange('date_month', 'date_year')
    def get_dates(self):
        today = fields.Date.today()
        date_year = int(self.date_year or today.year)
        date_month = int(self.date_month or today.month)
        date_ranges = calendar.monthrange(date_year, date_month)
        self.date_from = datetime.date(date_year, date_month, 1)
        self.date_to = datetime.date(date_year, date_month, date_ranges[1])
    
    def load_lines(self):
        statistics_obj = self.env['hr.employee.statistics']
        for rec in self:
            statistics_id = statistics_obj.create({
                'date_from': rec.date_from,
                'date_to': rec.date_to,
                'department_ids': [(6, 0, rec.department_ids.ids)],
                'company_id': rec.company_id.id,
            })
            # Load Employees
            statistics_id.load_dep_emp()
            # Create Lines
            statistics_id.load_lines()
            action = self.env.ref('hr_employee_statistics.hr_employee_statistics_action')
            result = action.read()[0]
            res = self.env.ref('hr_employee_statistics.hr_employee_statistics_form_view', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = statistics_id.id
            return result

# Ahmed Salama Code End.
