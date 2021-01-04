# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
PRICES = [('pricelist', 'List'),
          ('special1', 'Special 1'),
          ('special2', 'Special 2')]
FREIGHT = [('cf', 'CF'),
           ('lf', 'LF'),
           ('ec', 'DHL ec'),
           ('ex', 'DHL ex')]


class SaleOrderLineInherit(models.Model):
	_inherit = 'sale.order.line'
	
	pec_weight = fields.Float("Weight/pc kg", digits='Product Unit of Measure', help="Loaded from product static")
	moq = fields.Float("MOQ (pcs per box)", digits='Product Unit of Measure', help="Loaded from product static")
	special_price_1 = fields.Float('Very Special Price', digits='Product Price', help="Loaded from product static")
	special_price_2 = fields.Float('Special Price 2', digits='Product Price', help="Loaded from product static")
	customs = fields.Float('Customs(%)', digits='Product Price', help="Loaded from product static")
	
	ratio_fisher = fields.Float('Ratio fischer/BAT', digits='Product Price', )
	# Prices
	price_from = fields.Selection(PRICES, "Price", required=True, default='pricelist')
	total_cost = fields.Float("Total cost (USD)", digits='Product Price', compute='_compute_amount',
	                          help="Price * Order Qty (PCS)")
	price_piece_usd = fields.Float("Price unit per piece (USD/pcs)", digits='Product Price', compute='_compute_amount',
	                               help="Unit price / MOQ (pcs per box)")
	price_piece_sar = fields.Float("Price unit per piece (SAR/pcs)", digits='Product Price', compute='_compute_amount',
	                               help="Price unit per piece (USD/pcs) * 3.75")
	
	freight = fields.Selection(FREIGHT, "Freight", required=True, default='cf')
	lc_cf = fields.Float('LC CF(5%)', digits='Product Price', help="Loaded from product static")
	lc_lf = fields.Float('LC LF(15%)', digits='Product Price', help="Loaded from product static")
	lc_dhl_ec = fields.Float('LC DHL ec (6.85USD/kg)', digits='Product Price', help="Loaded from product static")
	lc_dhl_ex = fields.Float('LC DHL ex (8.01USD/kg)', digits='Product Price', help="Loaded from product static")
	
	landed_cost = fields.Float('landed Cost (SAR/pcs)', digits='Product Price', help="Loaded from product static")
	production_cost = fields.Float('Production cost (SAR/pcs)', digits='Product Price', help="Loaded from product static")
	alu_add_cost = fields.Float('Aluminum Additional Customs duty (SAR/pcs)', digits='Product Price'
	                            , help="Loaded from product static")
	landed_cost_sar = fields.Float("Landed Cost Price (SAR/pcs)", digits='Product Price', compute='_compute_amount',
	                               help="(Price unit per piece (SAR/pcs) * (1 + Customs(%)))"
	                                    " + landed Cost (SAR/pcs) + Aluminum Additional Customs duty (SAR/pcs)")
	
	selling_price = fields.Float('Selling Price to customer SR/PC', digits='Product Price')
	bat_margin_1 = fields.Float("BAT Margin(%)", digits='Product Price', compute='_compute_amount',
	                            help="(Selling Price to customer SR/PC - Landed Cost Price (SAR/pcs)) "
	                                 "/ Landed Cost Price (SAR/pcs)")
	landed_cost_margin = fields.Float("Total Cost  Price (landing cost without margin to BAT)",
	                                  digits='Product Price', compute='_compute_amount',
	                                  help="Landed Cost Price (SAR/pcs) * Order Qty (PCS)")
	total_selling_price = fields.Float("Total Selling Price",
	                                   digits='Product Price', compute='_compute_amount',
	                                   help="Selling Price to customer SR/PC * Order Qty (PCS)")
	bat_margin_2 = fields.Float("BAT Margin(%)", digits='Product Price', compute='_compute_amount',
	                                   help="(Total Selling Price - Total Cost  Price (landing cost without margin to BAT))"
	                                        "/Total Cost  Price (landing cost without margin to BAT)")
	final_margin = fields.Float("Final Margin(%)", digits='Product Price',)
	
	@api.onchange('price_from')
	def price_from_change(self):
		for line in self:
			if line.price_from == 'pricelist':
				line.price_unit = line.product_id.list_price
			elif line.price_from == 'special1':
				line.price_unit = line.product_id.special_price_1
			elif line.price_from == 'special2':
				line.price_unit = line.product_id.special_price_2
	
	@api.onchange('product_id')
	def product_id_change(self):
		"""
		Append default method to update line with product values
		:return: SUPER return
		"""
		res = super(SaleOrderLineInherit, self).product_id_change()
		product = {'moq': self.product_id.moq, 'special_price_1': self.product_id.special_price_1,
		           'special_price_2': self.product_id.special_price_2, 'customs': self.product_id.customs,
		           'lc_cf': self.product_id.lc_cf, 'lc_lf': self.product_id.lc_lf, 'lc_dhl_ec': self.product_id.lc_dhl_ec,
		           'lc_dhl_ex': self.product_id.lc_dhl_ex, 'production_cost': self.product_id.production_cost,
		           'alu_add_cost': self.product_id.alu_add_cost, 'ratio_fisher': self.product_id.ratio_fisher,
		           'landed_cost': self.product_id.landed_cost}
		if self.price_from == 'pricelist' and self.order_id.pricelist_id and self.order_id.partner_id:
			product['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
				self._get_display_price(self.product_id), self.product_id.taxes_id, self.tax_id, self.company_id)
		self.update(product)
		return res
	
	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id',
	             'customs', 'landed_cost', 'alu_add_cost', 'selling_price')
	def _compute_amount(self):
		"""
		Compute the amounts of the SO line.
		"""
		for line in self:
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
			                                product=line.product_id, partner=line.order_id.partner_shipping_id)
			total_cost = price * line.product_uom_qty
			price_per_piece_usd = line.moq and price / line.moq or 0.0
			price_per_piece_sar = price_per_piece_usd * 3.75
			landed_cost_sar = (price_per_piece_sar*(1+line.customs)) + line.landed_cost + line.alu_add_cost
			bat_margin_1 = landed_cost_sar and (line.selling_price-landed_cost_sar)/landed_cost_sar or 0.0
			landed_cost_margin = landed_cost_sar * line.product_uom_qty
			total_selling_price = line.selling_price * line.product_uom_qty
			bat_margin_2 = landed_cost_margin and (total_selling_price - landed_cost_margin)/landed_cost_margin or 0.0
			line.update({
				'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
				'total_cost': total_cost,
				'price_piece_usd': price_per_piece_usd,
				'price_piece_sar': price_per_piece_sar,
				'landed_cost_sar': landed_cost_sar,
				'bat_margin_1': bat_margin_1,
				'landed_cost_margin': landed_cost_margin,
				'total_selling_price': total_selling_price,
				'bat_margin_2': bat_margin_2,
			})
			if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
					'account.group_account_manager'):
				line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

# Ahmed Salama Code End.
