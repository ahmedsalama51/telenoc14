# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
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


class SaleOrderLineInherit(models.Model):
	_inherit = 'sale.order.line'
	
	# qty_available = fields.Float(related='product_id.qty_available', string="Qty Available", readonly=1, store=True)
	qty_available = fields.Float("Qty Available", compute='inventory_stock')
	qty_weight = fields.Float("Weight", help="Line Qty * Line UOM Bigger Ratio")
	
	@api.onchange('product_uom_qty', 'product_uom')
	def get_product_weight(self):
		"""
		Compute uom ratio weight in case of uom if from category weight
		:return:
		"""
		weight_categ_id = self.env.ref('uom.product_uom_categ_kgm')
		for line in self:
			if line.product_uom and line.product_uom.category_id == weight_categ_id:
				line.qty_weight = line.product_uom.factor_inv * line.product_uom_qty
	
	def inventory_stock(self):
		for rec in self:
			res1 = self.env['stock.quant']
			result = res1.search([('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id),
			                      ('product_id', '=', rec.product_id.id)], limit=1)
			_logger.info(red + 'result:' + str(result) + reset)
			if result:
				rec.qty_available = result.quantity - result.reserved_quantity
			else:
				rec.qty_available = 0
				
	@api.onchange('product_uom_qty')
	def _onchange_product_qty(self):
		for line in self:
			if line.product_id:
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
			if line.product_id:
				if float_compare(0, line.product_uom_qty, precision_digits=2) >= 0:
					raise Warning(_('Product %s quantity cannot Zero!!!' % line.product_id.display_name))
				if line.qty_available < line.product_uom_qty:
					raise Warning(_('Product %s demand quantity is over the available!' % line.product_id.display_name))

# Ahmed Salama Code End.
