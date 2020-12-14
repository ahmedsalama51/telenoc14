# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
_STATES = [('draft', 'Draft'),
           ('done', 'Done'),
           ('cancel', 'Cancel')]


class ReceiveCableRule(models.Model):
	_name = 'receive.cable.rule'
	_description = "Receive Cable Rules"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'date DESC'
	
	name = fields.Char("Number", readonly=1, default='/')
	active = fields.Boolean("Active", default=True, track_visibility='onchange')
	employee_id = fields.Many2one("hr.employee", "Receiver", track_visibility='onchange', readonly=1,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	location_id = fields.Many2one('stock.location', "Receive Location",
	                              check_company=True, readonly=True, required=True,
	                              states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	date = fields.Datetime("Date", default=fields.Datetime.now(), readonly=1, track_visibility='onchange',
	                       states={'draft': [('readonly', False)]}, help="Received Date")
	done_date = fields.Datetime("Done Date", readonly=1, help="Set Done Date", tracking=True)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True, readonly=1,
	                             states={'draft': [('readonly', False)]})
	product_id = fields.Many2one('product.product', 'Product', related='line_ids.product_id', readonly=True)
	line_ids = fields.One2many('receive.cable.rule.line', 'receive_id', "Lines",
	                           readonly=1, states={'draft': [('readonly', False)]})
	
	@api.model
	def create(self, vals):
		"""
		Add Seq for Receive
		:param vals: create vals
		:return: SUPER
		"""
		vals['name'] = self.env['ir.sequence'].sudo().next_by_code('receive.cable.rule.code')
		return super(ReceiveCableRule, self).create(vals)
	
	def action_done(self):
		"""
		- Set State to done
		- compute balance for line
		"""
		for rec in self:
			rec.state = 'done'
			rec.done_date = fields.Datetime.now()
			for line in rec.line_ids:
				line.balance_qty = line.receive_incoming_qty - (line.quantity + line.previous_qty)
	
	def action_cancel(self):
		"""
		Cancel receive
		"""
		for rec in self:
			rec.state = 'cancel'
	
	def action_draft(self):
		for rec in self:
			rec.state = 'draft'
			rec.done_date = False
			for line in rec.line_ids:
				line.balance_qty = 0.0
	
	@api.model
	def action_cable_balance_report(self):
		"""
		Collect all product lines to get it's last receive line order by balance amount
		:return: report
		"""
		receive_obj = self.env['receive.cable.rule']
		line_obj = self.env['receive.cable.rule.line']
		line_ids = []
		done_active_lines = line_obj.search([('receive_id.active', '=', True), ('receive_id.state', '=', 'done')])
		products = done_active_lines.mapped('product_id')
		for prod in products:
			last_prod_line = done_active_lines.search([('product_id', '=', prod.id)], order='date DESC', limit=1)
			if last_prod_line:
				receive_obj += last_prod_line.receive_id
				line_ids.append({
					'product_id': prod.id,
					'location_id': last_prod_line.location_id and last_prod_line.location_id.name or '',
					'name': prod.display_name,
					'quantity': last_prod_line.quantity,
					'uom_id': last_prod_line.product_uom and last_prod_line.product_uom.name or '',
					'receive_incoming_qty': last_prod_line.receive_incoming_qty,
					'previous_qty': last_prod_line.previous_qty,
					'total_after_qty': last_prod_line.total_after_qty,
					'balance_qty': last_prod_line.balance_qty,
				})
		data = {'date': str(fields.Date.today()),
		        'prod_count': len(products),
		        'doc_model': self.env['receive.cable.rule'],
		        'doc_ids': receive_obj.ids,
		        'docs': receive_obj,
		        'line_ids': sorted(line_ids, key=lambda i: i['balance_qty'], reverse=True)}
		return self.env.ref('electric_project_enhancement.report_receive_cable_rule_balance_act'). \
			with_context(landscape=True).report_action(self, data=data)


class ReceiveCableRuleLine(models.Model):
	_name = 'receive.cable.rule.line'
	_description = "Receive Cable Rule Lines"
	# TODO : Need to use location on filtration of oncoming shipments
	
	receive_id = fields.Many2one('receive.cable.rule', "Receive")
	location_id = fields.Many2one(related='receive_id.location_id')
	name = fields.Char(related='receive_id.name')
	state = fields.Selection(related='receive_id.state')
	date = fields.Datetime(related='receive_id.date')
	company_id = fields.Many2one(
		'res.company', 'Company',
		default=lambda self: self.env.company,
		index=True, required=True)
	product_id = fields.Many2one('product.product', 'Product', check_company=True, index=True, required=True,
	                             domain="[('type', 'in', ['product', 'consu']),"
	                                    " '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	quantity = fields.Float('Current Qty', digits='Product Unit of Measure', default=0.0, required=True,)
	product_uom = fields.Many2one('uom.uom', 'UOM', required=True,
	                              domain="[('category_id', '=', product_uom_category_id)]")
	product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
	receive_incoming_qty = fields.Float("Received From Checklist", compute='_get_qty',
	                                    help="All incoming shipment for this product")
	previous_qty = fields.Float("Previous Cables", compute='_get_qty',
	                            help="All previous received for it")
	balance_qty = fields.Float("Cable Balance", readonly=1,
	                           help="Balance = all incoming shipment for this product"
	                                " - (all previous received for it + current received qty)")
	total_after_qty = fields.Float("Total Received Cables", compute='_get_qty',
	                               help="Total After Received")
	note = fields.Text("Notes")
	
	@api.onchange('product_id')
	def onchange_product_id(self):
		self.product_uom = self.product_id.uom_id.id
	
	@api.onchange('product_id', 'quantity', 'date')
	@api.depends('receive_id.date')
	def _get_qty(self):
		"""
		Compute done moves before this move for same product & task
		"""
		ml_obj = self.env['stock.move']
		receive_obj = self.env['receive.cable.rule.line']
		for line in self:
			receive_incoming_qty = previous_qty = 0.0
			if line.product_id:
				incoming_ids = ml_obj.search([('product_id', '=', line.product_id.id),
				                              ('state', '=', 'done'),
				                              ('picking_type_id.code', '=', 'incoming'),
				                              ('location_dest_id', '=', line.location_id.id),
				                              ('date', '<=', line.date)])
				previous_qty = receive_obj.search([('product_id', '=', line.product_id.id),
				                                   ('state', '=', 'done'),
				                                   ('location_id', '=', line.location_id.id),
				                                   ('date', '<=', line.date)])
				receive_incoming_qty = sum(x.quantity_done for x in incoming_ids)
				previous_qty = sum(x.quantity for x in previous_qty.filtered(lambda mm: mm.id != line.id))
			line.receive_incoming_qty = receive_incoming_qty
			line.previous_qty = previous_qty
			line.total_after_qty = previous_qty + line.quantity
			line.balance_qty = receive_incoming_qty - (line.quantity + previous_qty)

# Ahmed Salama Code End.
