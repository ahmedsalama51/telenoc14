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
           ('cancel', 'Cancel')]
# Ahmed Salama Code Start ---->


class HrEmployeeRequestType(models.Model):
	_name = 'hr.employee.request.type'
	_description = "HR Employee Request Type"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_check_company_auto = True
	
	name = fields.Char("Request Type", required=True)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True)
	active = fields.Boolean(default=True)
	approval_cycle = fields.Selection([('one', 'One Approval'), ('two', 'Two Approvals')],
	                                  default='one', required=True, string="Approval Cycle")
	first_approve_group = fields.Many2one('res.groups', "First Approval Group")
	second_approve_group = fields.Many2one('res.groups', "Second Approval Group")
	req_date_start = fields.Boolean("Show/Required Date Start?", default=True)
	req_date_end = fields.Boolean("Show/Required Date End?")
	req_request_details = fields.Boolean("Show/Required Request Details?")
	line_ids = fields.One2many('hr.employee.request.type.line', 'type_id', "Approvals")
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	
	@api.model
	def default_get(self, fields):
		"""
		Load default manager groups
		:param fields: default dict
		:return: SUPER
		"""
		defaults = super(HrEmployeeRequestType, self).default_get(fields)
		hr_manager_group_id = self.env.ref('hr.group_hr_manager')
		defaults['first_approve_group'] = hr_manager_group_id and hr_manager_group_id.id or False
		defaults['second_approve_group'] = hr_manager_group_id and hr_manager_group_id.id or False
		return defaults


class HrEmployeeRequestTypeLine(models.Model):
	_name = 'hr.employee.request.type.line'
	_description = "HR Employee Request Type Line"
	_check_company_auto = True
	_rec_name = 'type_id'
	
	type_id = fields.Many2one('hr.employee.request.type', "Request Type", required=True, ondelete='cascade')
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True)
	department_id = fields.Many2one('hr.department', 'Department',
	                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	note = fields.Text("Note")
# Ahmed Salama Code End.
