# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
# Ahmed Salama Code Start ---->


class StockMoveInherit(models.Model):
	_inherit = 'stock.move'
	
	task_id = fields.Many2one('project.task', "Work Order", required=True)
	task_incoming_qty = fields.Float("Incoming Qty", compute='_get_task_qty')
	task_outgoing_qty = fields.Float("Outgoing Qty", compute='_get_task_qty')
	task_balance_qty = fields.Float("Balance Qty", compute='_get_task_qty')
	
	qty_available = fields.Float(related='product_id.qty_available', readonly=1)
	
	@api.onchange('state', 'product_id', 'task_id')
	def _get_task_qty(self):
		"""
		Compute done moves before this move for same product & task
		"""
		ml_obj = self.env['stock.move']
		for ml in self:
			task_incoming_qty = task_outgoing_qty = 0.0
			if ml.task_id:
				other_ml_ids = ml_obj.search([('product_id', '=', ml.product_id.id),
				                              ('task_id', '=', ml.task_id.id),
				                              ('state', '=', 'done'),
				                              ('date', '<=', ml.date)])
				task_incoming_qty = sum(x.quantity_done for x in other_ml_ids.
				                        filtered(lambda mm: mm.id != ml.id and mm.picking_type_id and
				                                            mm.picking_type_id.code == 'incoming'))
				task_outgoing_qty = sum(x.quantity_done for x in other_ml_ids.
				                        filtered(lambda mm: mm.id != ml.id and mm.picking_type_id and
				                                            mm.picking_type_id.code == 'outgoing'))
			ml.task_incoming_qty = task_incoming_qty
			ml.task_outgoing_qty = task_outgoing_qty
			ml.task_balance_qty = task_incoming_qty - task_outgoing_qty + ml.quantity_done


class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'
	
	task_id = fields.Many2one('project.task', "Work Order")
	
	task_incoming_qty = fields.Float("Incoming Qty", compute='_get_task_qty')
	task_outgoing_qty = fields.Float("Outgoing Qty", compute='_get_task_qty')
	task_balance_qty = fields.Float("Balance Qty", compute='_get_task_qty')
	
	qty_available = fields.Float(related='product_id.qty_available', readonly=1)
	
	@api.onchange('state', 'product_id', 'task_id')
	def _get_task_qty(self):
		"""
		Compute done moves before this move for same product & task
		"""
		sml_obj = self.env['stock.move.line']
		for sml in self:
			task_incoming_qty = task_outgoing_qty = 0.0
			if sml.task_id:
				other_sml_ids = sml_obj.search([('id', '!=', sml.id),
				                                ('product_id', '=', sml.product_id.id),
				                                ('task_id', '=', sml.task_id.id),
				                                ('state', '=', 'done'),
				                                ('date', '<=', sml.date)])
				task_incoming_qty = sum(x.qty_done for x in other_sml_ids.
				                        filtered(lambda ml: ml.move_id.picking_type_id and
				                                            ml.move_id.picking_type_id.code == 'incoming'))
				task_outgoing_qty = sum(x.qty_done for x in other_sml_ids.
				                        filtered(lambda ml: ml.move_id.picking_type_id and
				                                            ml.move_id.picking_type_id.code == 'outgoing'))
			sml.task_incoming_qty = task_incoming_qty
			sml.task_outgoing_qty = task_outgoing_qty
			sml.task_balance_qty = task_incoming_qty - task_outgoing_qty
	
	@api.model
	def default_get(self, field_list):
		result = super(StockMoveLineInherit, self).default_get(field_list)
		if self.move_id and self.move_id.task_id:
			result['task_id'] = self.move_id.task_id.id
		return result
	
	@api.model
	def create(self, vals):
		if vals.get('move_id'):
			move_id = self.env['stock.move'].browse(vals.get('move_id'))
			if move_id.task_id:
				vals['task_id'] = move_id.task_id.id
		return super(StockMoveLineInherit, self).create(vals)

# Ahmed Salama Code End.
