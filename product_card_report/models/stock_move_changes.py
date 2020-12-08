# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->


class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'
	
	@api.model
	def create(self, vals):
		"""
		Used to compute and store previous details
		"""
		line = super(StockMoveLineInherit, self).create(vals)
		#  compute and store previous details
		line.execute_update_history()
		return line
	
	pre_qty = fields.Float('Previous Qty', readonly=True, group_operator=False,
	                       help='Quantity in the default UoM of the product from previous moves')
	pre_cost = fields.Float('Previous Cost', readonly=True, group_operator=False,
	                        help='Cost from previous moves')
	curr_qty = fields.Float('Current Qty', readonly=True, group_operator=False,
	                        help='Quantity in the default UoM of the product from previous moves + current qty')
	curr_cost = fields.Float('Current Cost', readonly=True, group_operator=False,
	                         help='Cost from previous moves + current cost')
	signed_done_qty = fields.Float('Qty Done(+/-)', readonly=True,
	                               help='Quantity done amount with sign to use on total')
	price_unit = fields.Float('Unit Price', readonly=True, group_operator=False,
	                          help='Price used to compute line amount')
	
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
			_logger.info(green + "move: %s" % sml.reference + reset)
			# Location Field cases
			if sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == "outgoing":
				location_id = sml.location_id
			else:
				location_id = sml.location_dest_id
			domain = [('product_id', '=', sml.product_id.id),
			          ('date', '<=', sml.date),
			          ('state', '=', 'done')]
			if isinstance(sml.id, int):
				domain.append(('id', '!=', sml.id))
			_logger.info(red + "Domain: %s" % domain + reset)
			all_pre_move = sml_obj.search(domain,
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
			_logger.info(red + "Pre moves: %s" % pre_moves.mapped('reference') + reset)
			# Compute Signed Done Qty
			if sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == 'outgoing':
				signed_done_qty = -sml.qty_done
			else:
				signed_done_qty = sml.qty_done
			price = sml.move_id.price_unit or sml.product_id.standard_price
			_logger.info(red + "Price: %s" % price + reset)
			# compute extra fields
			if pre_moves:
				move_line_id = pre_moves[0]
				_logger.info(red + "pre move: %s  qty: %s  cost: %s signed qty: %s "
				             % (move_line_id.reference, move_line_id.curr_qty, move_line_id.curr_cost, signed_done_qty) + reset)
				pre_qty = move_line_id.curr_qty
				pre_cost = move_line_id.curr_cost
				after_qty = move_line_id.curr_qty + signed_done_qty
				after_cost = move_line_id.curr_cost + (signed_done_qty * price)
			else:
				pre_qty = 0.0
				pre_cost = 0.0
				after_qty = signed_done_qty
				after_cost = (signed_done_qty * price)
			sml.signed_done_qty = signed_done_qty
			sml.pre_qty = pre_qty
			sml.pre_cost = pre_cost
			sml.curr_qty = after_qty
			sml.curr_cost = after_cost
			sml.price_unit = price

# Ahmed Salama Code End.
