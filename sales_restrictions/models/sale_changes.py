# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
	

class SaleOrderLineInherit(models.Model):
	_inherit = 'sale.order.line'
	
	qty_available = fields.Float(related='product_id.qty_available', string="Qty Available", readonly=1, store=True)
	
	@api.onchange('product_uom_qty')
	def _onchange_product_qty(self):
		for line in self:
			if float_compare(0, line.product_uom_qty, precision_digits=2) >= 0:
				return {'warning': {'message': _('Product %s quantity cannot Zero!!!' % line.product_id.display_name)}}
			if line.qty_available < line.product_uom_qty:
				message = _('Product %s demand quantity is over the available!!!' % line.product_id.display_name)
				if line.qty_available:
					line.product_uom_qty = line.qty_available
					message += '\nIts set to available %s by default' % line.qty_available
				return {'warning': {'message': message}}
	
	@api.constrains('product_uom_qty', 'product_uos_qty')
	def constraint_qty(self):
		for line in self:
			if float_compare(0, line.product_uom_qty, precision_digits=2) >= 0:
				raise Warning(_('Product %s quantity cannot Zero!!!' % line.product_id.display_name))
			if line.qty_available < line.product_uom_qty:
				raise Warning(_('Product %s demand quantity is over the available!' % line.product_id.display_name))

# Ahmed Salama Code End.
