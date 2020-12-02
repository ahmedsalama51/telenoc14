# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
# Ahmed Salama Code Start ---->


class StockMoveInherit(models.Model):
	_inherit = 'stock.move'
	
	def _action_done(self, cancel_backorder=False):
		"""
		# Force use date from previous action as scheduled_date on move and move lines
		:param cancel_backorder:
		:return: SUPER moves
		"""
		moves_todo = super(StockMoveInherit, self)._action_done(cancel_backorder)
		for move in moves_todo:
			if move.date_deadline:
				move.write({'date': move.date_deadline})
				move.move_line_ids.write({'date': move.date_deadline})
		return moves_todo
	
		
class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'
	
	# TODO:: Stop this method and replace it with confirm for current fields/ Create for pre fields
	# @api.onchange('move_id', 'qty_done')
	# @api.depends('move_id.price_unit', 'move_id.picking_type_id', 'move_id.inventory_id')
	# def _get_product_historical_qty(self):
	# 	"""
	# 	Used to compute and store previous details
	# 	"""
	# 	_logger.info("\n -----------------------------------------------------\n"
	# 	             "Get historical qty and cost for %s" % len(self))
	# 	self.execute_update_history()
	
	@api.model
	def create(self, vals):
		"""
		Used to compute and store previous details
		"""
		line = super(StockMoveLineInherit, self).create(vals)
		# Force use date from move
		line.date = line.move_id.date
		#  compute and store previous details
		line.execute_update_history()
		return line
	
	pre_qty = fields.Float('Previous Qty', readonly=True,
	                       help='Quantity in the default UoM of the product from previous moves')
	pre_cost = fields.Float('Previous Cost', readonly=True,
	                        help='Cost from previous moves')
	curr_qty = fields.Float('Current Qty', readonly=True,
	                        help='Quantity in the default UoM of the product from previous moves + current qty')
	curr_cost = fields.Float('Current Cost', readonly=True,
	                         help='Cost from previous moves + current cost')
	signed_done_qty = fields.Float('Qty Done(+/-)', readonly=True,
	                               help='Quantity done amount with sign to use on total')
	price_unit = fields.Float(related='move_id.price_unit')
	
	@api.model
	def start_compute_historical_qty(self):
		_logger.info("\n -----------------------------------------------------\n start compute historical qty and cost")
		all_moves = self.env['stock.move.line'].search([])
		all_moves.set_product_historical_qty()
		_logger.info("\n -----------------------------------------------------\n all qty and cost fields are updated")
	
	def set_product_historical_qty(self):
		"""
		Used to re-compute and check for previous moves
		"""
		sml_obj = self.env['stock.move.line']
		records = self
		if not records and self.env.context.get('active_ids'):
			records = sml_obj.browse(self.env.context.get('active_ids'))
		_logger.info("\n -----------------------------------------------------\n"
		             "Set historical qty and cost for %s" % self.env.context.get('active_ids'))
		records.execute_update_history()
	
	def execute_update_history(self):
		"""
		- Filter current move to get location from it, to use it as ref on historical according to
			# Incoming -> destination field
			# Outgoing -> location field
			# Internal -> destination field
			# Inventory Adj -> destination field
		- use this location according to
			# Incoming -> destination field
			# Outgoing -> location field
			# Internal -> destination field
			# Inventory Adj -> destination field
		- Then Update records according to prev values
		"""
		sml_obj = self.env['stock.move.line']
		# TODO confirm that selected moves are ordered according to date not id
		for sml in self.sorted(lambda l: l.date):
			# Location Field cases
			if sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == "outgoing":
				location_id = sml.location_id
			else:
				location_id = sml.location_dest_id
			all_pre_move = sml_obj.search([('product_id', '=', sml.product_id.id),
			                               ('date', '<', sml.date),
			                               ('state', '=', 'done')],
			                              order="date DESC")
			pre_moves = sml_obj
			for h_move in all_pre_move:
				if h_move.move_id.picking_type_id and \
						h_move.move_id.picking_type_id.code == "outgoing" and \
						h_move.location_id == location_id:
					pre_moves += h_move
				elif h_move.move_id.picking_type_id and h_move.move_id.picking_type_id.code != "outgoing" and \
						h_move.location_dest_id == location_id:
					pre_moves += h_move
				elif h_move.move_id.inventory_id and \
						h_move.location_dest_id == location_id.id:
					pre_moves += h_move
			# Compute Signed Done Qty
			if sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == 'outgoing':
				signed_done_qty = -sml.qty_done
				price = sml.product_id.standard_price
			else:
				signed_done_qty = sml.qty_done
				price = sml.move_id.price_unit
			# compute extra fields
			if pre_moves:
				move_line_id = pre_moves[0]
				sml.pre_qty = move_line_id.curr_qty
				sml.pre_cost = move_line_id.curr_cost
				after_qty = move_line_id.curr_qty + signed_done_qty
				after_cost = move_line_id.curr_cost + (signed_done_qty * price)
			else:
				after_qty = signed_done_qty
				after_cost = (signed_done_qty * price)
			sml.signed_done_qty = signed_done_qty
			sml.curr_qty = after_qty
			sml.curr_cost = after_cost

# Ahmed Salama Code End.
