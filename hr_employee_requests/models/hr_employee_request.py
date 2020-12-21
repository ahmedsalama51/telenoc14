# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
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
           ('confirmed', 'Confirm'),
           ('first_approve', 'First Approved'),
           ('done', 'Approved'),
           ('dep_approvals', 'Dep. Approvals'),
           ('cancel', 'Cancel')]


# Ahmed Salama Code Start ---->


class HrEmployeeRequest(models.Model):
	_name = 'hr.employee.request'
	_description = "HR Employee Request"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_check_company_auto = True
	
	# Main Details
	name = fields.Char(default="/", readonly=1)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True, readonly=1,
	                             states={'draft': [('readonly', False)]})
	active = fields.Boolean(default=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	# Employee Details
	employee_id = fields.Many2one('hr.employee', "Employee", required=True, readonly=1,
	                              states={'draft': [('readonly', False)]}, tracking=True,
	                              default=lambda self: self.env.user.employee_id)
	identification_id = fields.Char(string='Identification No', tracking=True)
	department_id = fields.Many2one('hr.department', 'Department', tracking=True,
	                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	job_id = fields.Many2one('hr.job', 'Job Position', tracking=True,
	                         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	
	# Request Details
	type_id = fields.Many2one('hr.employee.request.type', "Request Type",
	                          required=True, ondelete='cascade', tracking=True)
	approval_cycle = fields.Selection(related='type_id.approval_cycle')
	req_date_start = fields.Boolean(related='type_id.req_date_start')
	req_date_end = fields.Boolean(related='type_id.req_date_end')
	req_request_details = fields.Boolean(related='type_id.req_request_details')
	date = fields.Datetime("Date", default=fields.Datetime.now(), readonly=1,
	                       states={'draft': [('readonly', False)]}, tracking=True)
	date_start = fields.Datetime("Start Date", default=fields.Datetime.now(), readonly=1,
	                             states={'draft': [('readonly', False)]}, tracking=True)
	date_end = fields.Datetime("End Date", readonly=1,
	                           states={'draft': [('readonly', False)]}, tracking=True)
	request_details = fields.Text("Request Details", tracking=True)
	line_ids = fields.One2many('hr.employee.request.line', 'request_id', "Approvals")
	show_first_approve = fields.Boolean(compute='show_approval_buttons')
	show_second_approve = fields.Boolean(compute='show_approval_buttons')
	show_success_badge = fields.Boolean(compute='show_approval_buttons')
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	
	@api.model
	def create(self, vals):
		"""
		Add Seq for Request
		:param vals: create vals
		:return: SUPER
		"""
		vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.employee.request.code')
		attend = super(HrEmployeeRequest, self).create(vals)
		return attend
	
	def write(self, vals):
		"""
		Message post that lines is loaded
		:param vals:
		:return:
		"""
		super(HrEmployeeRequest, self).write(vals)
		# if vals.get('line_ids'):
		# 	for req in self:
		# 		req.message_post(body="Load Type Approval Lines")
		return True
	
	@api.model
	def default_get(self, fields):
		"""
		Load default employee on open for create
		:param fields: default dict
		:return: SUPER
		"""
		defaults = super(HrEmployeeRequest, self).default_get(fields)
		if not defaults.get('employee_id'):
			employee_id = self.env.user.employee_id
			if not employee_id:
				raise Warning(
					_("Current user:%s ]\n have no related employee!!!, please check it first" % self.env.user.name))
			defaults['employee_id'] = employee_id.id
		employee_id = self.env['hr.employee'].browse(defaults.get('employee_id'))
		# Collect Employee details
		defaults['department_id'] = employee_id.department_id and employee_id.department_id.id or False
		defaults['job_id'] = employee_id.job_id and employee_id.job_id.id or False
		defaults['identification_id'] = employee_id.identification_id
		return defaults
	
	# --------------------------------------------------
	# Actions
	# --------------------------------------------------
	
	def action_confirm(self):
		"""
		- Confirm Details
		"""
		for rec in self:
			rec.state = 'confirmed'
	
	def action_done(self):
		"""
		- Hr manger approve sheet
		"""
		for rec in self:
			if rec.type_id.approval_cycle == 'one':
				if rec.line_ids and not all(app for app in rec.line_ids.mapped('is_approved')):
					rec.state = 'dep_approvals'
				else:
					rec.state = 'done'
			if rec.type_id.approval_cycle == 'two':
				if rec.state == 'confirmed':
					rec.state = 'first_approve'
				elif rec.state == 'first_approve':
					if rec.line_ids and not all(app for app in rec.line_ids.mapped('is_approved')):
						rec.state = 'dep_approvals'
					else:
						rec.state = 'done'
	
	def action_cancel(self):
		"""
		- Cancel Request
		"""
		for rec in self:
			rec.state = 'cancel'
	
	def action_draft(self):
		"""
		- reset state to draft
		"""
		for rec in self:
			rec.state = 'draft'
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	
	@api.onchange('employee_id')
	def onchange_employee_id(self):
		"""
		Get Default Employee Details
		:return:
		"""
		self.department_id = self.employee_id.department_id and self.employee_id.department_id.id or False
		self.job_id = self.employee_id.job_id and self.employee_id.job_id.id or False
		self.identification_id = self.employee_id.identification_id
	
	@api.onchange('type_id')
	def load_type_lines(self):
		"""
		Load type lines if exist
		"""
		for req in self:
			if req.type_id and req.type_id.line_ids:
				if req.line_ids:
					req.line_ids = [(5, 0)]
				line_ids = []
				for line in req.type_id.line_ids:
					line_ids.append((0, 0, {
						'request_id': req.id,
						'line_id': line.id,
						'department_id': line.department_id.id,
						'note': line.note,
					}))
				print("LINES:: ", line_ids)
				req.line_ids = line_ids
				req.message_notify(body="Load Type Approval Lines")
	
	@api.onchange('state', 'approval_cycle', 'line_ids')
	def show_approval_buttons(self):
		for req in self:
			show_first_approve = show_second_approve = show_success_badge = False
			if req.approval_cycle == 'one' and req.state == 'confirmed':
				show_second_approve = True
			elif req.approval_cycle == 'two' and req.state == 'confirmed':
				show_first_approve = True
			elif req.approval_cycle == 'two' and req.state == 'first_approve':
				show_second_approve = True
			req.show_first_approve = show_first_approve
			req.show_second_approve = show_second_approve
			if req.state == 'done':
				if not req.line_ids:
					show_success_badge = True
				elif all(app for app in req.line_ids.mapped('is_approved')):
					show_success_badge = True
			req.show_success_badge = show_success_badge


class HrEmployeeRequestLine(models.Model):
	_name = 'hr.employee.request.line'
	_description = "Request Approval Line"
	_check_company_auto = True
	_rec_name = 'request_id'
	
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True)
	request_id = fields.Many2one('hr.employee.request', "Request", ondelete='cascade')
	state = fields.Selection(related='request_id.state')
	line_id = fields.Many2one('hr.employee.request.type.line', "Type Line", required=True)
	department_id = fields.Many2one('hr.department', 'Department', readonly=True,
	                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	manager_id = fields.Many2one(related='department_id.manager_id')
	note = fields.Text("Note", readonly=True)
	user_id = fields.Many2one('res.users', "Name")
	is_approved = fields.Boolean("Approved?")
	approve_access = fields.Boolean("Approve Access?", compute='get_approve_access')
	approval_date = fields.Datetime("Approved Date")
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	
	def get_approve_access(self):
		"""
		Check if this current user have access to approve this line
		"""
		for line in self:
			approve_access = False
			print("department_id: ", self.env.user.employee_id,line.department_id.manager_id)
			if line.department_id and self.env.user.employee_id \
					and self.env.user.employee_id == line.department_id.manager_id:
				approve_access = True
			line.approve_access = approve_access
	
	@api.onchange('is_approved')
	def approve_log(self):
		"""
		Capture user and date to store on log of request
		"""
		for line in self:
			line.user_id = self.env.user
			line.approval_date = fields.Datetime.now()
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	def write(self, vals):
		"""
		message post for the action happened on line
		check state according to line approval rules
		:param vals:
		:return:
		"""
		super(HrEmployeeRequestLine, self).write(vals)
		for line in self:
			if 'is_approved' in vals:
				line.request_id.message_post(body="Approval of department %s changed as: <ul>"
				                                  "<li>Approved: %s</li>"
				                                  "<li>User: %s</li>"
				                                  "<li>Date: %s</li>"
				                                  "</ul>" % (
					                                  line.department_id.name, line.is_approved and "Yes" or "No",
					                                  line.user_id.name, line.approval_date))
				if line.is_approved and all(app for app in line.request_id.line_ids.mapped('is_approved')):
					line.request_id.state = 'done'
			# elif all(not app for app in line.request_id.line_ids.mapped('is_approved')):
			# 	if line.request_id.type_id.approval_cycle == 'one':
			# 		line.request_id.state = 'confirmed'
			# 	elif line.request_id.type_id.approval_cycle == 'two':
			# 		line.request_id.state = 'first_approve'
		return True

# Ahmed Salama Code End.
