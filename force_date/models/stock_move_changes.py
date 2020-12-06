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
			move.write({'date': move.date_expected})
			move.move_line_ids.write({'date': move.date_expected})
		return moves_todo
	
		
class StockMoveLineInherit(models.Model):
	_inherit = 'stock.move.line'
	
	@api.model
	def create(self, vals):
		"""
		Force use date from move
		"""
		line = super(StockMoveLineInherit, self).create(vals)
		line.date = line.move_id.date
		return line

# Ahmed Salama Code End.
