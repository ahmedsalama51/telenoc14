# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
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
			if move.picking_id:
				move_date = move.picking_id.scheduled_date
			else:
				move_date = move.date_deadline or move.date
			print("MOVE: DATE", move_date)
			if move_date:
				move.write({'date': move_date})
				move.move_line_ids.write({'date': move_date})
		return moves_todo
	
		
class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'

	@api.model
	def create(self, vals):
		"""
		Force use date from move
		"""
		move_id = self.env['stock.move'].browse(vals.get('move_id'))
		vals['date'] = move_id.date
			
		
		return super(StockMoveLineInherit, self).create(vals)

# Ahmed Salama Code End.
