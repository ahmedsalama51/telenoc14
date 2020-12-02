# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
# Ahmed Salama Code Start ---->


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	def _action_done(self):
		"""
		Used to :
		- compute and store previous details
		"""
		res = super(StockPickingInherit, self)._action_done()
		_logger.info("\n -----------------------------------------------------\n"
		             "Get historical qty and cost for %s" % len(self))
		for pick in self:
			# compute and store previous details
			pick.move_line_ids.execute_update_history()
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
				'date': picking.date
			})
	
	def action_picking_bulk_validate(self):
		"""
		Add An action to validate multi records on stock pickings
		:return: view with confirmed pickings
		"""
		picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids')).\
			filtered(lambda p: p.state not in ['done', 'cancel'] and p.show_validate)
		if picking_ids:
			print("PICKINGS:: ", picking_ids)
			transfer_obj = self.env['stock.immediate.transfer']
			wizard = transfer_obj.create({'pick_ids': picking_ids})
			wizard.sudo().process()
		
# Ahmed Salama Code End.

