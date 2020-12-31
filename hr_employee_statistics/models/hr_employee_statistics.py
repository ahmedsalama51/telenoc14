# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.tools import date_utils
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
	                        default=date_utils.start_of(fields.datetime.today(), 'month'),
	                        states={'draft': [('readonly', False)]}, tracking=True)
	date_to = fields.Date("Date To", required=True, readonly=True, tracking=True,
	                      default=date_utils.end_of(fields.datetime.today(), 'month'),
	                      states={'draft': [('readonly', False)]})
	department_ids = fields.Many2many('hr.department', string='Departments', readonly=True,
	                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
	                                  states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	line_ids = fields.One2many('hr.employee.statistics.line', 'statistics_id', "Lines")
	employee_id = fields.Many2one('hr.employee', "Employee", related='line_ids.employee_id', readonly=True)
	employee_ids = fields.Many2many('hr.employee', string="Employees",
	                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
	
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
				line.attend_line_ids = [(5, 0)]
	
	def action_draft(self):
		for rec in self:
			rec.state = 'draft'
			for line in rec.line_ids:
				line.state = 'draft'
	
	def load_dep_emp(self):
		"""
		Generate lines
		:return:
		"""
		for st in self:
			if st.department_ids:
				st.employee_ids = [(6, 0, st.department_ids.mapped('member_ids').ids)]
			else:
				st.employee_ids = [6, 0, self.env['hr.employee'].search([('contract_id', '=', False)])]
	
	def load_lines(self):
		"""
		Load Lines of this statistics
		:return:
		"""
		line_obj = self.env['hr.employee.statistics.line']
		attend_line_obj = self.env['hr.supervisor.attendance.line']
		for st in self:
			if st.employee_ids:
				st.line_ids = [(5, 0)]
				for emp in st.employee_ids:
					attend_lines = attend_line_obj.search([('employee_id', '=', emp.id),
					                                       ('date', '>=',  st.date_from),
					                                       ('date', '<=', st.date_to),
					                                       ('statistics_line_id', '=', False),
					                                       ('state', '=', 'done')])
					# if attend_lines:
					# 	print("==============\nEMPLOYEE:: ", emp.name)
					# 	print("LINES: ", attend_lines)
					# 	print("absent: ", sum(atl.overtime for atl in attend_lines))
					line_obj.create({
						'statistics_id': st.id,
						'employee_id': emp.id,
						'date_from': st.date_from,
						'date_to': st.date_to,
						'state': st.state,
						'overtime': sum(atl.overtime for atl in attend_lines),
						'absent_value': sum(atl.absent_value for atl in attend_lines),
						'attend_line_ids': [(6, 0, attend_lines.ids)],
					})
			else:
				raise Warning(_("No Employees selected to use!!!"))


class HrEmployeeStatisticsLine(models.Model):
	_name = 'hr.employee.statistics.line'
	_description = "HR Employee Statistics Lines"
	_check_company_auto = True
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'statistics_id'
	
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
	active = fields.Boolean('Active', default=True)
	statistics_id = fields.Many2one('hr.employee.statistics', "Statistics", ondelete='cascade')
	employee_id = fields.Many2one('hr.employee', "Employee", required=True, readonly=True,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	date_from = fields.Date("Date From", required=True, readonly=True,
	                        default=date_utils.start_of(fields.datetime.today(), 'month'),
	                        states={'draft': [('readonly', False)]}, tracking=True)
	date_to = fields.Date("Date To", required=True, readonly=True, tracking=True,
	                      default=date_utils.end_of(fields.datetime.today(), 'month'),
	                      states={'draft': [('readonly', False)]})
	absent_value = fields.Integer("Absent Value", readonly=True,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	overtime = fields.Float("Overtime", readonly=True,
	                        states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	attend_line_ids = fields.One2many('hr.supervisor.attendance.line', 'statistics_line_id', string="Attendance")
	
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
				domain = [('employee_id', '=', line.employee_id.id)]
				if isinstance(line.id, int):
					domain.append(('id', '!=', line.id))
				employee_lines = line_obj.search(domain)
				if line.date_from:
					if any(el.date_from <= line.date_from <= el.date_to for el in employee_lines):
						raise Warning(_("Date From: %s Collapse with pre statistics" % line.date_from))
				if line.date_to:
					if any(el.date_from <= line.date_to <= el.date_to for el in employee_lines):
						raise Warning(_("Date To: %s Collapse with pre statistics" % line.date_to))

# Ahmed Salama Code End.
