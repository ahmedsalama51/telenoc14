# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrPayslipInherit(models.Model):
	_inherit = 'hr.payslip'
	
	decision_payslip_increase = fields.Float("Admin Decision Increase", compute='calc_emp_statistics')
	decision_payslip_decrease = fields.Float("Admin Decision Decrease", compute='calc_emp_statistics')
	full_wage = fields.Float("Full Wage", compute='calc_emp_statistics')
	absent_value = fields.Integer("Absent Value", compute='calc_emp_statistics')
	overtime = fields.Float("Overtime", compute='calc_emp_statistics')
	
	@api.onchange('contract_id', 'date_from', 'date_to', 'employee_id')
	def calc_emp_statistics(self):
		"""
		Compute full details of this Employee on the selected period from statistics lines
		"""
		for payslip in self:
			statistics = self.env['hr.employee.statistics.line'].search([('employee_id', '=', payslip.employee_id.id),
			                                                            ('date_from', '<=', payslip.date_from),
			                                                            ('date_to', '>=', payslip.date_to),
			                                                            ('state', '=', 'done')], order='date_to DESC')
			payslip.decision_payslip_increase = sum(d.decision_payslip_increase for d in statistics)
			payslip.decision_payslip_decrease = sum(d.decision_payslip_decrease for d in statistics)
			payslip.full_wage = statistics and statistics[0].full_wage or 0.0
			payslip.absent_value = sum(d.absent_value for d in statistics)
			payslip.overtime = sum(d.overtime for d in statistics)
			

class HrSalaryRuleInherit(models.Model):
	_inherit = 'hr.salary.rule'
	amount_python_compute = fields.Text(default='''
	# Available variables:
    #----------------------
    # payslip: object containing the payslips
    # payslip params:
		- payslip.decision_payslip_increase
			---> Get sum of amounts of this payslip employee all full approved payslip increase administrative.decisions from statistics lines
		- payslip.decision_payslip_decrease
			---> Get sum of amounts of this payslip employee all full approved payslip decrease administrative.decisions from statistics lines
		- payslip.full_wage
			---> Get sum of wage of (this payslip employee all full approved payslip appraisal administrative.decisions + contract wage) from statistics lines
		- payslip.absent_value
			---> Get sum of absent days from statistics lines
		- payslip.overtime
			---> Get sum of overtime from statistics lines
	# employee: hr.employee object
    # contract: hr.contract object
    # rules: object containing the rules code (previously computed)
    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
    # worked_days: object containing the computed worked days.
    # inputs: object containing the computed inputs.

    # Note: returned value have to be set in the variable 'result'

    result = contract.wage * 0.10''')
# Ahmed Salama Code End.
