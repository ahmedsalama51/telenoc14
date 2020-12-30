# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrPayslipInherit(models.Model):
	_inherit = 'hr.payslip'
	
	decision_payslip_increase = fields.Float("Admin Decision Increase", compute='calc_admin_decisions')
	decision_payslip_decrease = fields.Float("Admin Decision Decrease", compute='calc_admin_decisions')
	full_wage = fields.Float("Full Wage", compute='calc_admin_decisions')
	
	@api.onchange('contract_id', 'date_from', 'date_to', 'employee_id')
	def calc_admin_decisions(self):
		for payslip in self:
			decisions = self.env['hr.administrative.decisions'].search([('employee_id', '=', payslip.employee_id.id),
			                                                            ('date', '>=', payslip.date_from),
			                                                            ('date', '<=', payslip.date_to),
			                                                            ('state', '=', 'second_approve')])
			payslip.decision_payslip_increase = sum(d.amount for d in decisions.
			                                        filtered(lambda l: l.decision_type_id.payroll_type == 'payslip_increase'))
			payslip.decision_payslip_decrease = sum(d.amount for d in decisions.
			                                        filtered(lambda l: l.decision_type_id.payroll_type == 'payslip_decrease'))
			payslip.full_wage = payslip.contract_id.wage + sum(p.amount for p
			                                                   in self.env['hr.administrative.decisions'].search([
				('employee_id', '=', self.employee_id.id),
				('date', '<=', self.date_from),
				('decision_type_id.payroll_type', '=', 'appraisal'),
				('state', '=', 'second_approve')]))
	
	def calc_admin_decision_payslip_increase(self):
		"""
		Get sum of amounts of this payslip employee all full approved payslip increase administrative.decisions
		:return: total
		"""
		self.ensure_one()
		return sum(p.amount for p in
		           self.env['hr.administrative.decisions'].search([('employee_id', '=', self.employee_id.id),
		                                                           ('date', '>=', self.date_from),
		                                                           ('date', '<=', self.date_to),
		                                                           ('decision_type_id.payroll_type', '=', 'payslip_increase'),
		                                                           ('state', '=', 'second_approve')]))
	
	def calc_admin_decision_payslip_decrease(self):
		"""
		Get sum of amounts of this payslip employee all full approved payslip decrease administrative.decisions
		:return: total
		"""
		self.ensure_one()
		return sum(p.amount for p in
		           self.env['hr.administrative.decisions'].search([('employee_id', '=', self.employee_id.id),
		                                                           ('date', '>=', self.date_from),
		                                                           ('date', '<=', self.date_to),
		                                                           ('decision_type_id.payroll_type', '=', 'payslip_decrease'),
		                                                           ('state', '=', 'second_approve')]))
	
	def calc_full_wage(self):
		"""
		Get sum of wage of this payslip employee all full approved payslip appraisal administrative.decisions + contract wage
		:return: total
		"""
		self.ensure_one()
		full_appraisals = sum(p.amount for p
		                      in self.env['hr.administrative.decisions'].search([('employee_id', '=', self.employee_id.id),
		                                                                         ('date', '<=', self.date_from),
		                                                                         ('decision_type_id.payroll_type', '=', 'appraisal'),
		                                                                         ('state', '=', 'second_approve')]))
		return self.contract_id.wage + full_appraisals


class HrSalaryRuleInherit(models.Model):
	_inherit = 'hr.salary.rule'
	amount_python_compute = fields.Text(default='''
	# Available variables:
    #----------------------
    # payslip: object containing the payslips
    # payslip params/methods:
		- payslip.decision_payslip_increase OR payslip.calc_admin_decision_payslip_increase()
			---> Get sum of amounts of this payslip employee all full approved payslip increase administrative.decisions
		- payslip.decision_payslip_decrease OR payslip.calc_admin_decision_payslip_decrease()
			---> Get sum of amounts of this payslip employee all full approved payslip decrease administrative.decisions
		- payslip.full_wage OR payslip.calc_full_wage()
			---> Get sum of wage of this payslip employee all full approved payslip appraisal administrative.decisions + contract wage
	# employee: hr.employee object
    # contract: hr.contract object
    # rules: object containing the rules code (previously computed)
    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
    # worked_days: object containing the computed worked days.
    # inputs: object containing the computed inputs.

    # Note: returned value have to be set in the variable 'result'

    result = contract.wage * 0.10''')
# Ahmed Salama Code End.
