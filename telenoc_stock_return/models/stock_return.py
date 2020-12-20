# -*- coding: utf-8 -*-

import logging

import requests

from odoo import models, fields, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->
_STATES = [('draft', 'Draft'),
           ('ready', 'Ready'),
           ('done', 'Done'),
           ('cancel', 'Cancel')]


class StockReturn(models.Model):
	_name = 'stock.return'
	_description = "Stock Return"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_check_company_auto = True
	
	name = fields.Char(default="/", readonly=1)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True, readonly=1,
	                             states={'draft': [('readonly', False)]})
	active = fields.Boolean(default=True)
	state = fields.Selection(_STATES, "State", default='draft', tracking=True)
	date = fields.Datetime("Date", default=fields.Datetime.now(), readonly=1,
	                       states={'draft': [('readonly', False)]}, tracking=True)
	done_date = fields.Datetime("Done Date", readonly=1, tracking=True)
	picking_id = fields.Many2one('stock.picking', 'Operation', readonly=True,)
	picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, readonly=True,
	                                  states={'draft': [('readonly', False)]})
	location_id = fields.Many2one(
		'stock.location', 'Source Location', dauto_join=True, index=True, required=True, check_company=True, tracking=True)
	location_dest_id = fields.Many2one(
		'stock.location', 'Destination Location', auto_join=True, index=True, required=True, check_company=True, tracking=True)
	line_ids = fields.One2many('stock.return.line', 'return_id', "Products", readonly=1,
	                           states={'draft': [('readonly', False)]})
	notes = fields.Text("Notes", tracking=True)
	transfer_type = fields.Selection([('return', 'Returns'), ('internal', 'Internal')], "Transfer Type")
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].sudo().next_by_code('stock.return.code')
		return super(StockReturn, self).create(vals)
	
	# --------------------------------------------------
	# Actions
	# --------------------------------------------------
	def action_transfer(self):
		"""
		- reset state to draft
		"""
		picking_object = self.env['stock.picking']
		for rec in self:
			picking_vals = rec._prepare_separated_picking()
			rec.picking_id = picking_object.create(picking_vals)
			if rec.picking_id:
				rec.picking_id.action_confirm()
				rec.state = 'ready'
				rec.line_ids.write({'state': 'ready'})
	
	def action_done(self):
		"""
		- Hr manger/supervisor cancel sheet
		"""
		transfer_obj = self.env['stock.immediate.transfer']
		for rec in self:
			if rec.picking_id:
				if rec.picking_id.state in ['waiting', 'confirmed']:
					rec.picking_id.action_assign()
				if rec.picking_id.state == 'assigned':
					transfer_obj.create({'pick_ids': rec.picking_id}).process()
				if rec.picking_id.state == 'done':
					rec._action_done()
				else:
					raise Warning(_("Couldn't validate picking due to Inventory restriction\n"
					                "Please review picking and try to validate it first."))
				rec.done_date = fields.Datetime.now()
			else:
				raise Warning(_("No Operation to validate!!!"))
	
	def action_cancel(self):
		"""
		- Hr manger/supervisor cancel sheet
		"""
		for rec in self:
			if rec.picking_id:
				rec.picking_id.action_cancel()
			rec.state = 'cancel'
			rec.line_ids.write({'state': 'cancel'})
	
	def action_draft(self):
		"""
		- reset state to draft
		"""
		for rec in self:
			rec.state = 'draft'
			rec.line_ids.write({'state': 'draft'})
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	
	def _prepare_separated_picking(self):
		return {
			# collect picking data
			'picking_type_id': self.picking_type_id.id,
			'scheduled_date': self.date,
			'date': self.date,
			'origin': "Stock Return",
			'location_id': self.location_id and self.location_id.id or False,
			'location_dest_id': self.location_dest_id and self.location_dest_id.id or False,
			'company_id': self.company_id.id,
			'return_id': self.id,
			'move_ids_without_package':
				[(0, 0, {
					# collect lines data
					'name': (line.product_id.display_name or '')[:2000],
					'return_line_id': line.id,
					'product_id': line.product_id.id,
					'product_uom': line.product_uom.id,
					'product_uom_qty': line.quantity,
					'date': self.date,
					'date_deadline': self.date,
					'location_id': self.location_id and self.location_id.id or False,
					'location_dest_id': self.location_dest_id and self.location_dest_id.id or False,
					'state': 'draft',
					'company_id': line.company_id and line.company_id.id or False,
					'price_unit': line.price_unit,
					'picking_type_id': self.picking_type_id and self.picking_type_id.id or False,
					'origin': "Stock Return",
					# 'warehouse_id': self.location_id.warehouse_id and self.location_id.warehouse_id.id or False,
				}) for line in self.line_ids]
		}
	
	@api.model
	def default_get(self, fields_list):
		"""
		GET default internal transfer for active company
		:param fields_list:
		:return:
		"""
		defaults = super(StockReturn, self).default_get(fields_list)
		default_type_id = self.env['stock.picking.type'].search([('code', '=', 'internal'),
		                                                         '|', ('company_id', '=', self.env.company.id),
		                                                         ('company_id', '=', False)], limit=1)
		defaults['picking_type_id'] = default_type_id and default_type_id.id or False
		return defaults
	
	def _action_done(self):
		"""
		Mark object and line as done
		"""
		self.state = 'done'
		self.line_ids.write({'state': 'done'})


class StockReturnLine(models.Model):
	_name = 'stock.return.line'
	_description = "Stock Return Lines"
	_check_company_auto = True
	_rec_name = 'product_id'
	
	return_id = fields.Many2one('stock.return', 'Return', ondelete='cascade')
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
	                             index=True, required=True, readonly=1,
	                             states={'draft': [('readonly', False)]})
	location_id = fields.Many2one(related='return_id.location_id')
	state = fields.Selection(_STATES, "State", default='draft')
	product_id = fields.Many2one(
		'product.product', 'Product',
		check_company=True,
		domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
		index=True, required=True, readonly=1, states={'draft': [('readonly', False)]})
	quantity = fields.Float('Return', digits='Product Unit of Measure',
	                        default=0.0, required=True,  readonly=1, states={'draft': [('readonly', False)]})
	product_uom = fields.Many2one('uom.uom', 'UOM', required=True,
	                              domain="[('category_id', '=', product_uom_category_id)]"
	                              , readonly=1, states={'draft': [('readonly', False)]})
	product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
	availability = fields.Float(
		'Available', compute='_compute_product_availability',
		readonly=True, help='Quantity in stock that can still be reserved for this source location\n'
		                    'after deduct current quantity')
	price_unit = fields.Float('Unit Price', compute='_get_product_price', store=True,
	                          help="Get return price:\n"
	                               "-Case 1: Move that have same inverse source & destination locations with price > 0.\n"
	                               "-Case 2: Move that have current source location as destination on it with price > 0.\n"
	                               "-Case 3: Cost price from product (Current Cost).")
	price_description = fields.Text("Price Details", store=True, compute='_get_product_price')
	note = fields.Text("Notes")
	
	@api.onchange('product_id')
	def onchange_product_id(self):
		self.product_uom = self.product_id.uom_id.id
	
	@api.onchange('state', 'product_id', 'quantity', 'location_id')
	@api.depends('return_id.location_id')
	def _compute_product_availability(self):
		""" Fill the `availability` field on a stock move, which is the quantity to potentially
		reserve. When the move is done, `availability` is set to the quantity the move did actually
		move.
		"""
		for line in self:
			if line.state == 'done':
				line.availability = line.quantity
			else:
				available = self.env['stock.quant']._get_available_quantity(
					line.product_id,  line.location_id) if line.product_id else 0.0
				line.availability = available - line.quantity
	
	@api.onchange('product_id', 'location_id')
	@api.depends('return_id.location_id', 'return_id.location_dest_id')
	def _get_product_price(self):
		"""
		Get product price from :
		- Case 1: Move that have same inverse source & destination locations with price > 0.
	    - Case 2: Move that have current source location as destination on it with price > 0.
	    - Case 3: Cost price from product (Current Cost).
		"""
		stock_move_obj = self.env['stock.move']
		for line in self:
			price = 0.0
			price_description = ""
			if line.product_id:
				# Case 1:
				move_id = stock_move_obj.search([('product_id', '=', line.product_id.id),
				                                 ('return_line_id', '=', False),
				                                 ('location_id', '=', line.return_id.location_dest_id.id),
				                                 ('location_dest_id', '=', line.return_id.location_id.id),
				                                 ('price_unit', '>', 0)], limit=1, order='date DESC,id DESC')
				if move_id:
					print("1 move_id.price_unit: ", move_id.price_unit)
					price = move_id.price_unit
					price_description = "Price from exact move: %s" % move_id.reference
					_logger.info(green + "\n -----------------------------------------------------\n"
					                     "Price from exact inverse move %s" % move_id.reference + reset)
				else:
					# Case 2:
					move_id = stock_move_obj.search([('product_id', '=', line.product_id.id),
					                                 ('return_line_id', '=', False),
					                                 ('location_dest_id', '=', line.return_id.location_id.id),
					                                 ('price_unit', '>', 0)], limit=1, order='date DESC,id DESC')
					if move_id:
						print("2  move_id.price_unit: ",  move_id.price_unit)
						price = move_id.price_unit
						price_description = "Price from destination move: %s" % move_id.reference
						_logger.info(blue + "\n -----------------------------------------------------\n"
						                    "Price from inverse destination move %s" % move_id.reference + reset)
					else:
						# Case 3
						price = line.product_id.standard_price
						price_description = "Price from product cost"
						_logger.info(yellow + "\n -----------------------------------------------------\n"
						                      "Price from product cost" + reset)
			line.price_unit = price
			line.price_description = price_description

# Ahmed Salama Code End.
