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
	
	def get_material_balance(self):
		"""
		Get move lines balance for report Work Order Material Balance
		:return: List of product details
		"""
		product_ids = self.move_line_ids.mapped('product_id')
		material_balance = []
		for prod in product_ids:
			move_line_ids = self.move_line_ids.filtered(lambda m: m.product_id == prod and m.state == 'done')
			incoming = sum(m.qty_done for m in move_line_ids.filtered(lambda ml: ml.move_id.picking_type_id.code == 'incoming'))
			outgoing = sum(m.qty_done for m in move_line_ids.filtered(lambda ml: ml.move_id.picking_type_id.code == 'outgoing'))
			balance = incoming - outgoing
			material_balance.append({
				'product_code': prod.default_code,
				'product_name': prod.name,
				'unit': prod.uom_id and prod.uom_id.name or '',
				'incoming': incoming,
				'outgoing': outgoing,
				'needs': balance < 0 and balance or 0.0,
				'returns': balance > 0 and balance or 0.0,
			})
		return material_balance
	
	def get_material_moves(self):
		"""
		Get move lines for report Work Order Material moves
		:return: List of move line details
		"""
		material_moves = []
		for move_line in self.move_line_ids. \
				filtered(lambda ml: ml.move_id.picking_type_id.code in ['incoming', 'outgoing']). \
				sorted(lambda ml: (ml.product_id, ml.date)):
			material_moves.append({
				'product_code': move_line.product_id.default_code,
				'product_name': move_line.product_id.name,
				'unit': move_line.product_id.uom_id and move_line.product_id.uom_id.name or '',
				'type': move_line.move_id.picking_type_id.code,
				'ref': move_line.reference,
				'date': move_line.date,
				'qty': move_line.qty_done,
			})
		return material_moves


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
