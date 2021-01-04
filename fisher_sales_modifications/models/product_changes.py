# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ProductTemplateInherit(models.Model):
	_inherit = 'product.template'
	
	pec_weight = fields.Float("Weight/pc kg", digits='Product Unit of Measure',)
	moq = fields.Float("MOQ (pcs per box)", digits='Product Unit of Measure',)
	special_price_1 = fields.Monetary('Very Special Price', digits='Product Price',)
	special_price_2 = fields.Monetary('Special Price 2', digits='Product Price',)
	customs = fields.Float('Customs(%)', digits='Product Price',)
	lc_cf = fields.Float('LC CF(5%)', digits='Product Price',)
	lc_lf = fields.Float('LC LF(15%)', digits='Product Price',)
	lc_dhl_ec = fields.Float('LC DHL ec (6.85USD/kg)', digits='Product Price',)
	lc_dhl_ex = fields.Float('LC DHL ex (8.01USD/kg)', digits='Product Price',)
	landed_cost = fields.Float('landed Cost (SAR/pcs)', digits='Product Price', )
	production_cost = fields.Float('Production cost (SAR/pcs)', digits='Product Price', )
	alu_add_cost = fields.Float('Aluminum Additional Customs duty (SAR/pcs)', digits='Product Price',)
	ratio_fisher = fields.Float('Ratio fischer/BAT', digits='Product Price',)
	
	@api.onchange('pec_weight')
	def _compute_product_lc(self):
		for product in self:
			if product.pec_weight:
				product.lc_dhl_ec = product.pec_weight * 6.85
				product.lc_dhl_ex = product.pec_weight * 8.01

# Ahmed Salama Code End.
