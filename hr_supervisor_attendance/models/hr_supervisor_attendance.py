# -*- coding: utf-8 -*-

import logging

import requests

from odoo import models, fields, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->
_STATES = [('draft', 'Draft'),
           ('attended', 'Attended'),
           ('overtime', 'Overtime Checked'),
           ('done', 'Confirmed'),
           ('cancel', 'Cancel')]


class HRSupervisorAttendance(models.Model):
	_name = 'hr.supervisor.attendance'
	_description = "HR Supervisor Attendance"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'date, employee_id'
	
	employee_id = fields.Many2one('hr.employee', "Supervisor", requied=True, readonly=1,
	                              states={'draft': [('readonly', False)]},
	                              default=lambda self: self.env.user.employee_id)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True, readonly=1,
	                             states={'draft': [('readonly', False)]})
	name = fields.Char(default="/", readonly=1)
	state = fields.Selection(_STATES, "State", default='draft')
	date = fields.Datetime("Date", default=fields.Datetime.now(), readonly=1,
	                       states={'draft': [('readonly', False)]})
	line_ids = fields.One2many('hr.supervisor.attendance.line', 'super_attend_id', "Employees", readonly=1,
	                           states={'draft': [('readonly', False)], 'attended': [('readonly', False)],
	                                   'overtime': [('readonly', False)]})
	notes = fields.Text("Notes")
	active = fields.Boolean(default=True)
	# GET LOCATION ON MAPS TODO:: replace this with mobile app futures
	location = fields.Char("Location", compute='get_location')
	dimension = fields.Char("Dimension", compute='get_location')
	location_url = fields.Char(compute='get_location')
	
	# Access Writes
	edit_ability = fields.Boolean("Can Edit?", default=False, compute='edit_ability_check')
	
	# Totals
	absent_count = fields.Integer("Total Absent", compute='amount_total')
	total_overtime = fields.Float("Total Overtime", compute='amount_total')
	
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
		vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.supervisor.attendance.code')
		attend = super(HRSupervisorAttendance, self).create(vals)
		return attend
	
	@api.model
	def default_get(self, fields):
		"""
		Load default employee on open for create
		:param fields: default dict
		:return: SUPER
		"""
		defaults = super(HRSupervisorAttendance, self).default_get(fields)
		if not defaults.get('employee_id'):
			employee_id = self.env.user.employee_id
			if not employee_id:
				raise Warning(
					_("Current user:%s ]\n have no related employee!!!, please check it first" % self.env.user.name))
			defaults['employee_id'] = employee_id.id
		employee_id = self.env['hr.employee'].browse(defaults.get('employee_id'))
		defaults['line_ids'] = [(0, 0, {'employee_id': child.id, 'state': 'draft'})
		                        for child in employee_id.child_ids]
		return defaults
	
	# --------------------------------------------------
	# Actions
	# --------------------------------------------------
	
	def action_attended(self):
		"""
		- Supervisor add attendance to all emp
		"""
		for rec in self:
			rec.state = 'attended'
			rec.line_ids.write({'state': 'attended'})
	
	def action_overtime(self):
		"""
		- Supervisor add overtime to all emp
		"""
		for rec in self:
			rec.state = 'overtime'
			rec.line_ids.write({'state': 'overtime'})
	
	def action_done(self):
		"""
		- Hr manger approve sheet
		"""
		for rec in self:
			rec.state = 'done'
			rec.line_ids.write({'state': 'done'})
	
	def action_cancel(self):
		"""
		- Hr manger/supervisor cancel sheet
		"""
		for rec in self:
			rec.state = 'cancel'
			rec.line_ids.write({'state': 'cancel'})
	
	def action_draft(self):
		"""
		- reset state to draft
		"""
		for rec in self:
			rec.state = 'draft'
			rec.line_ids.write({'state': 'draft'})
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	
	# @api.onchange('employee_id')
	def load_supervisor_employees(self):
		"""
		Load employees that this supervisor is supervise on them
		:return: in case of have no child raise warning
		"""
		if self.line_ids:
			# Remove old lines to reload them
			self.line_ids = [(5, 0)]
		
		if self.employee_id.child_ids:
			# Create new lines
			self.line_ids = self._get_default_child_list()
		else:
			raise Warning(_("This Employee: %s]\n have no supervised employees!!! " % self.employee_id.name))
	
	def _get_default_child_list(self):
		"""
		GET LIST OF LINES
		:return:
		"""
		if self.employee_id.child_ids:
			# Create new lines
			return [(0, 0, {'super_attend_id': self.id,
			                'employee_id': child.id}) for child in self.employee_id.child_ids]
	
	@api.onchange('employee_id')
	def get_location(self):
		url = 'http://ipinfo.io/json'
		r = requests.get(url)
		js = r.json()
		self.dimension = js['loc']
		city = js['city']
		region = js['region']
		country_code = js['country']
		country_id = self.env['res.country'].search([('code', '=', country_code)], limit=1)
		self.location = "%s, %s, %s" % (city, region, country_id and country_id.name or country_code)
		location_url = "https://maps.google.com/maps?hl=en" \
		               "&ie=UTF8&z=12&iwloc=B&output=embed"
		if self.dimension:
			location_url += "&q=%s" % self.dimension
		self.location_url = location_url
	
	@api.onchange('line_ids')
	@api.depends('line_ids.absent', 'line_ids.overtime')
	def amount_total(self):
		for attend in self:
			attend.absent_count = len(attend.line_ids.filtered(lambda l: l.absent))
			attend.total_overtime = sum(l.overtime for l in attend.line_ids)
	
	@api.onchange('date')
	def _apply_date_on_lines(self):
		for attend in self:
			if attend.date and attend.line_ids:
				attend.line_ids.write({'date': attend.date})
	
	def edit_ability_check(self):
		"""
		Give Ability to edit only to HR manger users
		:return:
		"""
		for attend in self:
			edit_ability = False
			if self.env.user.has_group('hr.group_hr_manager'):
				edit_ability = True
			attend.edit_ability = edit_ability


class HRSupervisorAttendanceLine(models.Model):
	_name = 'hr.supervisor.attendance.line'
	_description = "HR Supervisor Attendance Employee"
	_rec_name = 'name'
	
	name = fields.Char("Name", readonly=1)
	super_attend_id = fields.Many2one('hr.supervisor.attendance', 'Supervisor Attendance', ondelete='cascade')
	employee_id = fields.Many2one('hr.employee', "Employee", requied=True)
	state = fields.Selection(_STATES, "State", default='draft', readonly=True)
	absent = fields.Boolean("Absent", help="Checked if employee is absent", readonly=1, group_operator='bool_and',
	                        states={'draft': [('readonly', False)]})
	absent_value = fields.Integer("Absent Value", readonly=False)
	overtime = fields.Float("Overtime", help="Add Overtime")
	note = fields.Text("Note")
	date = fields.Datetime('Date')
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	@api.model
	def create(self, vals):
		"""
		Assign name and date
		:param vals: create vals
		:return: super
		"""
		if 'absent' in vals:
			vals['absent_value'] = 1 and vals.get('absent') or 0
		line = super(HRSupervisorAttendanceLine, self).create(vals)
		if line.super_attend_id:
			line.date = line.super_attend_id.date
			line.name = "%s-%s" % (line.super_attend_id.name, line.employee_id.name)
		return line
	
	def write(self, vals):
		if 'absent' in vals:
			vals['absent_value'] = 1 and vals.get('absent') or 0
		return super(HRSupervisorAttendanceLine, self).write(vals)
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	@api.constrains('employee_id', 'date')
	def employee_date_constrain(self):
		"""
		Employee Constrain not to be duplicate on same day
		"""
		line_obj = self.env['hr.supervisor.attendance.line']
		for attend in self:
			# Getting correct date
			# old_tz = timezone('UTC')
			# tz = self.env.user.tz
			# tz = timezone(tz)
			# attend_date = old_tz.localize(attend.super_attend_id.date).astimezone(tz)
			# ('date', '>=', attend_date.replace(hour=0, minute=0, second=0, microsecond=0)),
			# ('date', '<=', attend_date.replace(hour=23, minute=59, second=59))]
			if attend.employee_id:
				domain = [('employee_id', '=', attend.employee_id.id),
				          (
				          'date', '>=', attend.super_attend_id.date.replace(hour=0, minute=0, second=0, microsecond=0)),
				          ('date', '<=', attend.super_attend_id.date.replace(hour=23, minute=59, second=59))]
				if isinstance(attend.id, int):
					domain.append(('id', '!=', attend.id))
				other_attendance = line_obj.search(domain)
				_logger.info(red + "Constrain Domain:: %s" % domain + reset)
				_logger.info(yellow + "other_attendance:: %s" % other_attendance + reset)
				if other_attendance:
					raise Warning(_("Employee: %s Can't have move than 1 attend on same day.\n others: %s" %
					                (attend.employee_id.name, other_attendance.mapped('name'))))

# Ahmed Salama Code End.
