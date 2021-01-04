# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ProductTemplateInherit(models.Model):
	_inherit = 'product.template'
	
	moq = fields.Float("MOQ (pcs per box)", digits='Product Unit of Measure',)
	special_price_1 = fields.Float('Very Special Price', digits='Product Price',)
	special_price_2 = fields.Float('Special Price 2', digits='Product Price',)
	customs = fields.Float('Customs(%)', digits='Product Price',)
	lc_cf = fields.Float('LC CF(5%)', digits='Product Price',)
	lc_lf = fields.Float('LC LF(15%)', digits='Product Price',)
	lc_dhl = fields.Float('LC DHL', digits='Product Price',)
	production_cost = fields.Float('Production Cost', digits='Product Price',)
	alu_add_cost = fields.Float('Aluminum Additional Customs duty (SAR/pcs)', digits='Product Price',)
	ratio_fisher = fields.Float('Ratio fischer/BAT', digits='Product Price',)

# Ahmed Salama Code End.