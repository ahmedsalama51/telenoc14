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
	signed_done_qty = fields.Float('Qty Done(+/-)', readonly=True, group_operator='sum',
	                               help='Quantity done amount with sign to use on total')
	in_qty = fields.Float("Qty In", readonly=True, group_operator='sum',
	                      help='Quantity done amount with sign +, which received to warehouse')
	out_qty = fields.Float("Qty Out", readonly=True, group_operator='sum',
	                       help='Quantity done amount with sign -, which sent from warehouse')
	price_unit = fields.Float('Unit Price', readonly=True, group_operator=False,
	                          help='Price used to compute line amount')
	last_move_ref = fields.Char("Previous Ref")
	move_type = fields.Char("Move Type")
	special_case = fields.Boolean("Special Cases")
	# main_uom_id = fields.Many2one('uom.uom', 'Main Uom')
	category_id = fields.Many2one(related='product_uom_id.category_id')
	main_price_unit = fields.Float('Price(Main UOM)', readonly=True, group_operator=False,
	                               help='Price on main unit of measure used to compute line amount')
	
	@api.model
	def update_all_product_historical_qty(self):
		"""
		Used to re-compute and check for previous moves(All moves checked)
		"""
		_logger.info(green + "\n -----------------------------------------------------\n"
		                     " start compute all moves lines historical qty and cost" + reset)
		all_moves = self.env['stock.move.line'].search([])
		all_moves.set_product_historical_qty()
		_logger.info(green + "\n -----------------------------------------------------\n"
		                     " all qty and cost fields are updated" + reset)
	
	def set_product_historical_qty(self):
		"""
		Used to re-compute and check for previous moves(Only checked)
		"""
		sml_obj = self.env['stock.move.line']
		records = self
		if not records and self.env.context.get('active_ids'):
			records = sml_obj.browse(self.env.context.get('active_ids'))
		_logger.info(blue + "\n -----------------------------------------------------\n"
		                    "Set historical qty and cost for %s" % records.mapped('reference') + reset)
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
		ordered_records = self.sorted(lambda l: (l.date, l.id))
		# _logger.info(blue + "Records:: %s" % ordered_records.mapped('reference') + reset)
		for sml in ordered_records:
			_logger.info(green + "move: %s" % sml.reference + reset)
			# Location Field cases
			location_id = False
			if sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == "outgoing":
				# Outgoing ---> use current source in filters
				location_id = sml.location_id
				move_type = 'Outgoing'
			elif sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == "incoming":
				# Incoming ---> use current destination in filters
				location_id = sml.location_dest_id
				move_type = 'Incoming'
			elif sml.move_id.picking_type_id and sml.move_id.picking_type_id.code == "internal":
				# internal ---> use current destination in filters
				move_type = 'Internal'
				if sml.location_id.usage == 'internal':
					location_id = sml.location_id
					_logger.info(blue + "--- USED INTERNAL SRC LOCATION: %s" % location_id.name + reset)
				elif sml.location_dest_id.usage == 'internal':
					location_id = sml.location_dest_id
					_logger.info(blue + "--- USED INTERNAL DEST LOCATION: %s" % location_id.name + reset)
				else:
					_logger.info(red + "--- non of LOCATION is ready to use" + reset)
					# Slip this line
					continue
			
			else:
				# Inventory use internal location as it's
				if sml.location_id.usage == 'internal':
					location_id = sml.location_id
				elif sml.location_dest_id.usage == 'internal':
					location_id = sml.location_dest_id
				# _logger.info(yellow + "Inv1 Location  %s" % location_id + reset)
				move_type = 'Adjust'
			_logger.info(yellow + "move_type: %s" % move_type + reset)
			domain = [('product_id', '=', sml.product_id.id),
			          ('date', '<=', sml.date),
			          ('state', '=', 'done')]
			if isinstance(sml.id, int):
				domain.append(('id', '!=', sml.id))
			# _logger.info(yellow + "--- Domain: %s" % domain + reset)
			all_pre_move = sml_obj.search(domain, order="date DESC, id DESC")
			# _logger.info(yellow + "--- all_pre_move: %s" % all_pre_move.mapped('reference') + reset)
			_logger.info(yellow + "--- LOCATION: %s" % location_id.name + reset)
			pre_moves = sml_obj
			for h_move in all_pre_move:
				if h_move.date == sml.date and h_move.id > sml.id:
					_logger.info(yellow + "Removed  %s" % h_move.reference + reset)
					continue
				if h_move.move_id.picking_type_id:
					
					if h_move.move_id.picking_type_id.code == "outgoing" and h_move.location_id == location_id:
						# ADD search for previous Outgoing and it's src location in current location
						pre_moves += h_move
					elif h_move.move_id.picking_type_id.code == "incoming" and h_move.location_dest_id == location_id:
						# ADD search for previous Incoming/Internals and it's dest location in current location
						pre_moves += h_move
					elif h_move.move_id.picking_type_id.code == "internal":
						# _logger.info(yellow + "--- %s_move: %s, location: %s, dest location: %s"
						#              % (h_move.move_id.picking_type_id.code, h_move.reference,
						#                 h_move.location_id.id, h_move.location_dest_id.id) + reset)
						if h_move.location_dest_id == location_id or h_move.location_id == location_id:
							# ADD search for previous Incoming/Internals and it's dest location in current location
							pre_moves += h_move
				elif h_move.move_id.inventory_id:
					# Inventory use internal location as it's
					inv_location_id = False
					if h_move.location_id.usage == 'internal':
						inv_location_id = h_move.location_id
					elif h_move.location_dest_id.usage == 'internal':
						inv_location_id = h_move.location_dest_id
					# _logger.info(yellow + "Inv2 Location %s move: %s" % (inv_location_id, h_move.reference) + reset)
					if inv_location_id and inv_location_id == location_id:
						pre_moves += h_move
			# Compute Signed Done Qty
			if move_type == 'Outgoing':
				# outgoing so qty will decrease
				_logger.info(bold_red + " outgoing so qty will decrease" + reset)
				signed_done_qty = -sml.qty_done
			elif move_type == 'Adjust' and sml.location_id.usage == 'internal':
				_logger.info(bold_red + " it's inventory adjust with - so it will deduct from location" + reset)
				# it's inventory adjust with - so it will deduct from location
				signed_done_qty = -sml.qty_done
			elif move_type == 'Adjust' and sml.location_dest_id.usage == 'internal':
				_logger.info(bold_red + "it's inventory adjust with - so it will increase to location" + reset)
				# it's inventory adjust with - so it will increase to location
				signed_done_qty = sml.qty_done
			elif move_type == 'Internal' and sml.location_id.usage == 'internal':
				# it's internal with - so it will deduct from location
				_logger.info(bold_red + "it's internal with - so it will deduct from location" + reset)
				signed_done_qty = -sml.qty_done
			elif move_type == 'Internal' and sml.location_dest_id.usage == 'internal':
				# it's internal with - so it will increase to location
				_logger.info(bold_red + "it's internal with - so it will increase to location" + reset)
				signed_done_qty = sml.qty_done
			else:
				# inventory +/- qty will add to for now --> TODO:: NEED TO CHECK for inventory adjust of - qty
				# incoming or internal qty will add to for now , SPECIAL CASE WILL HANDLE SEPARATE
				_logger.info(bold_red + "it'sdoesn't found any of above" + reset)
				signed_done_qty = sml.qty_done
			_logger.info(yellow + "signed_done_qty: %s" % signed_done_qty + reset)
			price = sml.move_id.price_unit or sml.product_id.standard_price
			# compute extra fields
			if pre_moves:
				# Sort pre moves
				pre_moves = pre_moves.sorted(lambda l: (l.date, l.id), reverse=True)
				# _logger.info(yellow + "Pre moves: %s" % pre_moves.mapped('reference') + reset)
				move_line_id = pre_moves[0]
				_logger.info(yellow + "pre move: %s  qty: %s  cost: %s signed qty: %s "
				             % (move_line_id.reference, move_line_id.curr_qty, move_line_id.curr_cost,
				                signed_done_qty) + reset)
				# CHECK FOR SPECIAL CASES
				special_case = False
				if move_line_id.move_id.picking_type_id and move_line_id.move_id.picking_type_id.code == 'internal':
					if move_type == 'Outgoing' and sml.location_id == move_line_id.location_id:
						special_case = True
					if move_type == 'Incoming' and sml.location_dest_id == move_line_id.location_id:
						special_case = True
					if move_type == 'Internal' and sml.location_dest_id == move_line_id.location_id:
						special_case = True
					if move_type == 'Internal' and sml.location_id == move_line_id.location_id:
						special_case = True
				if special_case:
					_logger.info(
						red + "Special Case: %s, previous: %s" % (sml.reference, move_line_id.reference) + reset)
					pre_qty, pre_cost, after_qty, after_cost = sml._compute_special_case(move_line_id, move_type,
					                                                                     signed_done_qty, price,
					                                                                     pre_moves)
				else:
					pre_qty = move_line_id.curr_qty
					pre_cost = move_line_id.curr_cost
					after_qty = move_line_id.curr_qty + signed_done_qty
					after_cost = move_line_id.curr_cost + (signed_done_qty * price)
				last_move_ref = move_line_id.reference
			else:
				pre_qty = 0.0
				pre_cost = 0.0
				after_qty = signed_done_qty
				after_cost = (signed_done_qty * price)
				last_move_ref = False
				special_case = False
			sml.signed_done_qty = signed_done_qty
			sml.pre_qty = pre_qty
			sml.pre_cost = pre_cost
			sml.curr_qty = after_qty
			sml.curr_cost = after_cost
			sml.price_unit = price
			sml.main_price_unit = price * sml.product_uom_id.factor_inv
			sml.last_move_ref = last_move_ref
			sml.move_type = move_type
			sml.special_case = special_case
			sml.in_qty = signed_done_qty > 0 and abs(signed_done_qty) or 0.0
			sml.out_qty = signed_done_qty < 0 and abs(signed_done_qty) or 0.0
	
	def _compute_special_case(self, move_line_id, move_type, signed_done_qty, price, all_previous):
		"""
		Compute actual qty in case of previous is internal
		:param move_line_id:
		:param move_type:
		:return: pre_qty, pre_cost, after_qty, after_cost
		"""
		sml_obj = internal_moves = self.env['stock.move.line']
		location = False
		if move_type == 'Outgoing' and self.location_id == move_line_id.location_id:
			location = self.location_id
		elif move_type == 'Incoming' and self.location_dest_id == move_line_id.location_id:
			location = self.location_dest_id
		elif move_type == 'Internal' and self.location_dest_id == move_line_id.location_id:
			location = self.location_id
		elif move_type == 'Internal' and self.location_id == move_line_id.location_id:
			location = self.location_dest_id
		_logger.info(red + "Special location: %s" % location.id + reset)
		
		# this move is outgoing but pre is internal and should decrease from it's source
		# STEP1: will get it's last move exclude internal moves
		domain = [('product_id', '=', self.product_id.id),
		          ('date', '<=', self.date),
		          ('state', '=', 'done')]
		if isinstance(self.id, int):
			domain.append(('id', '!=', self.id))
		all_previous = sml_obj.search(domain, order="date DESC, id DESC").filtered(lambda l: l.location_id == location or l.location_dest_id == location)
		_logger.info(red + "Special Case previous: %s" % all_previous.mapped('reference') + reset)
		last_move_id = False
		for pre_move in all_previous:
			if pre_move.date == self.date and pre_move.id > self.id:
				_logger.info(red + "Special Removed  %s" % pre_move.reference + reset)
				continue
			elif pre_move.move_id.picking_type_id and \
					pre_move.move_id.picking_type_id.code == 'internal' and location == pre_move.location_id:
				_logger.info(red + "Special intern(-)  %s" % pre_move.reference + reset)
				internal_moves += pre_move
			else:
				_logger.info(red + "Special LAST  %s" % pre_move.reference + reset)
				last_move_id = pre_move
				break
		if not last_move_id and internal_moves:
			last_move_id = internal_moves[0]
		if last_move_id:
			_logger.info(red + "Special Case last_move_id: %s" % last_move_id.reference + reset)
		
		# we will count on last move value but deduct/increase internal amounts
		after_qty = last_move_id and last_move_id.curr_qty or 0
		after_cost = last_move_id and last_move_id.curr_cost or 0
		_logger.info(red + "Special after_qty: %s" % after_qty + reset)
		# STEP2: decrease handle internals out of this location between those period
		if internal_moves:
			_logger.info(red + "Special internal_moves: %s" % internal_moves.mapped('reference') + reset)
			for internal_move in internal_moves:
				int_signed_qty = 0.0
				int_price = internal_move.move_id.price_unit or internal_move.product_id.standard_price
				if internal_move.location_dest_id == location:
					int_signed_qty = internal_move.qty_done
				elif internal_move.location_id == location:
					int_signed_qty = -internal_move.qty_done
				
				_logger.info(red + "Special int_location:%s int_dest: %s int_signed_qty: %s"
				             % (internal_move.location_id.id, internal_move.location_dest_id.id, int_signed_qty) + reset)
				after_qty += int_signed_qty
				after_cost += int_signed_qty * int_price
		return after_qty, after_cost, (after_qty + signed_done_qty), after_qty + (signed_done_qty*price)

# Ahmed Salama Code End.
