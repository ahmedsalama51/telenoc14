# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
	

class SaleOrderLineInherit(models.Model):
	_inherit = 'sale.order.line'
	
	moq = fields.Float("MOQ (pcs per box)", digits='Product Unit of Measure', )
	special_price_1 = fields.Float('Very Special Price', digits='Product Price', )
	special_price_2 = fields.Float('Special Price 2', digits='Product Price', )
	customs = fields.Float('Customs(%)', digits='Product Price', )
	lc_cf = fields.Float('LC CF(5%)', digits='Product Price', )
	lc_lf = fields.Float('LC LF(15%)', digits='Product Price', )
	lc_dhl = fields.Float('LC DHL', digits='Product Price', )
	production_cost = fields.Float('Production Cost', digits='Product Price', )
	alu_add_cost = fields.Float('Aluminum Additional Customs duty (SAR/pcs)', digits='Product Price', )
	ratio_fisher = fields.Float('Ratio fischer/BAT', digits='Product Price', )
	
	@api.onchange('product_id')
	def product_id_change(self):
		"""
		Append default method to update line with product values
		:return: SUPER return
		"""
		res = super(SaleOrderLineInherit, self).product_id_change()
		product = {'moq': self.product_id.moq, 'special_price_1': self.product_id.special_price_1,
		           'special_price_2': self.product_id.special_price_2, 'customs': self.product_id.customs,
		           'lc_cf': self.product_id.lc_cf, 'lc_lf': self.product_id.lc_lf, 'lc_dhl': self.product_id.lc_dhl,
		           'production_cost': self.product_id.production_cost, 'alu_add_cost': self.product_id.alu_add_cost,
		           'ratio_fisher': self.product_id.ratio_fisher}
		self.update(product)
		return res

# Ahmed Salama Code End.
