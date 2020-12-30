# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
_STATES = [('draft', 'Draft'),
           ('done', 'Done'),
           ('cancel', 'Cancel')]


class HrEmployeeStatistics(models.Model):
	_name = 'hr.employee.statistics'
	_description = "HR Employee Statistics"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_check_company_auto = True
	
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
	active = fields.Boolean('Active', default=True)
	name = fields.Char("Statistics", readonly=True)
	date_from = fields.Date("Date From", required=True, readonly=True,
	                        states={'draft': [('readonly', False)]}, tracking=True)
	date_to = fields.Date("Date To", required=True, readonly=True,
	                      states={'draft': [('readonly', False)]}, tracking=True)
	department_id = fields.Many2one('hr.department', 'Department', readonly=True,
	                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
	                                states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	line_ids = fields.One2many('hr.employee.statistics.line', 'statistics_id', "Lines")
	employee_id = fields.Many2one('hr.employee', "Employee", related='line_ids.employee_id', readonly=True)
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	@api.model
	def create(self, vals):
		"""
		Add Seq for Receive
		:param vals: create vals
		:return: SUPER
		"""
		vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.employee.statistics.code')
		return super(HrEmployeeStatistics, self).create(vals)
		
	# --------------------------------------------------
	# Actions
	# --------------------------------------------------
	
	def action_done(self):
		"""
		- Set State to done
		- compute balance for line
		"""
		for rec in self:
			rec.state = 'done'
			for line in rec.line_ids:
				line.state = 'draft'
	
	def action_cancel(self):
		"""
		Cancel receive
		"""
		for rec in self:
			rec.state = 'cancel'
			for line in rec.line_ids:
				line.state = 'draft'
	
	def action_draft(self):
		for rec in self:
			rec.state = 'draft'
			for line in rec.line_ids:
				line.state = 'draft'
	
	def load_lines(self):
		pass


class HrEmployeeStatisticsLine(models.Model):
	_name = 'hr.employee.statistics.line'
	_description = "HR Employee Statistics Lines"
	_check_company_auto = True
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
	active = fields.Boolean('Active', default=True)
	statistics_id = fields.Many2one('hr.employee.statistics', "Statistics", ondelete='cascade')
	employee_id = fields.Many2one('hr.employee', "Employee", required=True, readonly=True,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	date_from = fields.Date("Date From", required=True, readonly=True,
	                        states={'draft': [('readonly', False)]}, tracking=True)
	date_to = fields.Date("Date To", required=True, readonly=True,
	                      states={'draft': [('readonly', False)]}, tracking=True)
	absent_value = fields.Integer("Absent Value", readonly=True,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	overtime = fields.Float("Overtime", readonly=True,
	                        states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	@api.constrains('employee_id', 'date_from', 'date_to')
	def _constrain_avoid_collapse(self):
		"""
		Constrain to avoid any collapse of those employee line with previous lines
		"""
		line_obj = self.env['hr.employee.statistics.line']
		for line in self:
			if line.employee_id:
				employee_lines = line_obj.search([('employee_id', '=', line.employee_id.id)])
				if line.date_from:
					if any(el.date_from <= line.date_from <= el.date_to for el in employee_lines):
						raise Warning(_("Date From: %s Collapse with pre statistics" % line.date_from))
				if line.date_to:
					if any(el.date_from <= line.date_to <= el.date_to for el in employee_lines):
						raise Warning(_("Date To: %s Collapse with pre statistics" % line.date_to))

# Ahmed Salama Code End.
