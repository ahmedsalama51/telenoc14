# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrPayslipInherit(models.Model):
	_inherit = 'hr.payslip'
	
	absent_value = fields.Integer("Absent Value", compute='calc_emp_attendance')
	overtime = fields.Float("Overtime", compute='calc_emp_attendance')
	
	@api.onchange('date_from', 'date_to', 'employee_id')
	def calc_emp_attendance(self):
		for payslip in self:
			attendance = self.env['hr.supervisor.attendance.line'].search([('employee_id', '=', payslip.employee_id.id),
			                                                               ('date', '>=', payslip.date_from),
			                                                               ('date', '<=', payslip.date_to),
			                                                               ('state', '=', 'done')])
			
			payslip.absent_value = sum(d.absent_value for d in attendance)
			payslip.overtime = sum(d.overtime for d in attendance)


class HrSalaryRuleInherit(models.Model):
	_inherit = 'hr.salary.rule'
	amount_python_compute = fields.Text(default='''
	# Available variables:
    #----------------------
    # payslip: object containing the payslips
    # payslip params:
		- payslip.absent_value
			---> Get sum of absent days from attendance lines
		- payslip.overtime
			---> Get sum of overtime from attendance lines
	# employee: hr.employee object
    # contract: hr.contract object
    # rules: object containing the rules code (previously computed)
    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
    # worked_days: object containing the computed worked days.
    # inputs: object containing the computed inputs.

    # Note: returned value have to be set in the variable 'result'

    result = contract.wage * 0.10''')
# Ahmed Salama Code End.
