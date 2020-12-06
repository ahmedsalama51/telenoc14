# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
# Ahmed Salama Code Start ---->


class SaleOrderInherit(models.Model):
	_inherit = 'sale.order'
	
	def action_confirm(self):
		"""
		Replace Core method to stop change date_order to current date
		:return:
		"""
		if self._get_forbidden_state_confirm() & set(self.mapped('state')):
			raise UserError(_(
				'It is not allowed to confirm an order in the following states: %s'
			) % (', '.join(self._get_forbidden_state_confirm())))
		
		for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
			order.message_subscribe([order.partner_id.id])
		# EDITES: Stop change date order on confirm
		self.write({
			'state': 'sale',
			# 'date_order': fields.Datetime.now()
		})
		self._action_confirm()
		if self.env.user.has_group('sale.group_auto_done_setting'):
			self.action_done()
		self.picking_ids.write({'date': self.date_order,
		                        'scheduled_date': self.date_order})
		return True

# Ahmed Salama Code End.
