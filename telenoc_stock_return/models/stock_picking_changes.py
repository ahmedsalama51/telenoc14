# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class StockMoveInherit(models.Model):
	_inherit = 'stock.move'
	
	return_line_id = fields.Many2one('stock.return.line', "Transfer Line", readonly=True,
	                            help="Source return line that used to create this operation")


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	return_id = fields.Many2one('stock.return', "Transfer", readonly=True,
	                            help="Source return that used to create this operation")
	
	def write(self, vals):
		"""
		While set state to done mark return also as done if exist
		:param vals:
		:return: SUPER
		"""
		for picking in self:
			if vals.get('state') == 'done' and picking.return_id:
				picking.return_id._action_done()
		return super(StockPickingInherit, self).write(vals)
# Ahmed Salama Code End.