# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ProjectTaskInherit(models.Model):
	_inherit = 'project.task'
	
	work_order_class_id = fields.Many2one('work.order.class', "Work Class",
	                                      help="تصنيف المعاملة")
	work_order_type_id = fields.Many2one('work.order.type', "Work Type",
	                                     help="نوع المعاملة")


class WorkOrderClass(models.Model):
	_name = 'work.order.class'
	_description = "Work Order Class"
	
	name = fields.Char('class')
	active = fields.Boolean("Active", default=True)


class WorkOrderType(models.Model):
	_name = 'work.order.type'
	_description = "Work Order Type"
	
	name = fields.Char('Type')
	active = fields.Boolean("Active", default=True)
	tags_ids = fields.Many2many('work.order.type.tag', "Tags")


class WorkOrderTypeTa(models.Model):
	_name = 'work.order.type.tag'
	_description = "Work Order Type Tag"
	
	name = fields.Char('Type Tag')
	color = fields.Integer("Color")

# Ahmed Salama Code End.
