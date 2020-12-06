# -*- coding: utf-8 -*-
import logging

from odoo import models, api

_logger = logging.getLogger(__name__)

# Ahmed Salama Code Start ---->


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	def action_done(self):
		"""
		Used to :
		- force date done with schedule date
		"""
		res = super(StockPickingInherit, self).action_done()
		for pick in self:
			pick.date_done = pick.date
		return res
	
	@api.onchange('date')
	def _compute_scheduled_date(self):
		"""
		Replace core code with new one to depend on previous action date
		:return:
		"""
		for picking in self:
			picking.scheduled_date = picking.date
			picking.move_lines.write({
				'date_expected': picking.date,
				'date': picking.date
			})

# Ahmed Salama Code End.

