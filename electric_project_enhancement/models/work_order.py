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
	move_ids = fields.One2many('stock.move', 'task_id', "Operations")
	move_line_ids = fields.One2many('stock.move.line', 'task_id', "Detailed Operations")
	operation_count = fields.Integer("Operation Count", compute='compute_operations')
	details_operation_count = fields.Integer("Detailed Operation Count", compute='compute_operations')
	
	@api.onchange('move_ids', 'move_line_ids')
	def compute_operations(self):
		"""
		compute related fields
		"""
		for task in self:
			task.operation_count = len(task.move_ids)
			task.details_operation_count = len(task.move_line_ids)
	
	def action_view_stock_move_lines(self):
		self.ensure_one()
		action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
		action['domain'] = [('task_id', '=', self.id)]
		return action
	
	def action_view_stock_moves(self):
		self.ensure_one()
		action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_action")
		action['domain'] = [('task_id', '=', self.id)]
		return action


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
