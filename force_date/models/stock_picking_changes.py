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
	
	@api.model
	def create(self, vals):
		picking = super(StockPickingInherit, self).create(vals)
		print("PICKING: ", picking.scheduled_date, picking.date)
		if picking.scheduled_date and\
					picking.scheduled_date != picking.date:
			picking.date = vals.get('scheduled_date')
			picking.date_deadline = vals.get('scheduled_date')
		return picking
	
	@api.onchange('name', 'sale_is')
	def _compute_scheduled_date(self):
		"""
		Replace core code with new one to depend on previous action date
		:return:
		"""
		print("HERE-------")
		for picking in self:
			print(" picking.date: ",  picking.date)
			print(" picking.scheduled_date: ",  picking.scheduled_date)
			picking.scheduled_date = picking.date
			picking.move_lines.write({
				'date_deadline': picking.date,
				'date': picking.date
			})
			
	def write(self, vals):
		for picking in self:
			if vals.get('scheduled_date') or vals.get('date') or vals.get('date_deadline'):
				if picking.scheduled_date and \
						picking.scheduled_date != picking.date:
					scheduled_date = vals.get('scheduled_date') or picking.scheduled_date
					if scheduled_date:
						vals['date'] = scheduled_date
						vals['date_deadline'] = scheduled_date
		return super(StockPickingInherit, self).write(vals)

# Ahmed Salama Code End.

