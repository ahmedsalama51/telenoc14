# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->


class StockPickingTypeInherit(models.Model):
	_inherit = 'stock.picking.type'
	
	allow_separate = fields.Boolean("Auto Separate?",
	                                help="Used to separate internal pickings into 2 pickings\n"
	                                     "- from SRC location to (pre defined virtual location) auto validated\n"
	                                     "- from (pre defined virtual location) to DEST location")
	separate_location_id = fields.Many2one('stock.location', check_company=True, domain=[('usage', '=', 'transit')],
	                                       help="Middle location used to separate internal moves into 2 operations\n"
	                                            "- from SRC location to (pre defined virtual location) auto validated\n"
	                                            "- from (pre defined virtual location) to DEST location")


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	allow_separate = fields.Boolean("Auto Separate?",
	                                help="Used to separate internal pickings into 2 pickings\n"
	                                     "- from SRC location to (pre defined virtual location) auto validated\n"
	                                     "- from (pre defined virtual location) to DEST location")
	separated_picking_id = fields.Many2one('stock.picking', "Separated Picking", readonly=True,
	                                       help="Used to show other separated part")
	is_separated = fields.Boolean("Is Separated?",
	                              help="Used to show if this picking which allowed to separated is separated or not yet.")
	
	# --------------------------------------------------
	# CRUD
	# --------------------------------------------------
	@api.model
	def create(self, vals):
		"""
		Set field allow_separate according to picking type
		"""
		if vals.get('picking_type_id'):
			picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
			if picking_type_id.code == 'internal':
				vals['allow_separate'] = picking_type_id.allow_separate
		return super(StockPickingInherit, self).create(vals)
	# --------------------------------------------------
	# Actions
	# --------------------------------------------------
	
	def action_done(self):
		"""
		Used to :
		- compute and store previous details
		"""
		res = super(StockPickingInherit, self).action_done()
		_logger.info(blue + "\n -----------------------------------------------------\n"
		                    "Get historical qty and cost for %s" % len(self) + reset)
		for pick in self:
			# compute and store previous details
			pick.move_line_ids.execute_update_history()
		return res
	
	def action_picking_bulk_validate(self):
		"""
		Add An action to validate multi records on stock pickings
		:return: view with confirmed pickings
		"""
		_logger.error(blue + "Start validate picking with ids: %s" % self.env.context.get('active_ids') + reset)
		picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids')) \
			.filtered(lambda p: p.state not in ['done', 'cancel'])
		# TODO:: Mark As to do for draft items
		draft_pickings = picking_ids.filtered(lambda p: p.state == 'draft')
		results = "<ul>"
		# Mark as to do ready pickings
		if draft_pickings:
			for pick in draft_pickings:
				try:
					pick.action_confirm()
					results += "<li style='color:green'>%s is Mark as todo successfully</li>" % pick.name
				except Exception as e:
					results += "<li style='color:red'>%s picking not Mark as todo due to:<br/>%s</li>" % (pick.name, e)
					_logger.error(red + "%s picking not Mark as todo due to:\n %s" % (pick.name, e) + reset)
		waiting_pickings = picking_ids.filtered(lambda p: p.state in ['waiting', 'confirmed'])
		# Check availability for waiting
		if waiting_pickings:
			for pick in waiting_pickings:
				try:
					pick.action_assign()
					results += "<li style='color:green'>%s is check availability successfully</li>" % pick.name
				except Exception as e:
					results += "<li style='color:red'>%s picking not check availability due to:<br/> %s</li>" % (pick.name, e)
					_logger.error(red + "%s picking not check availability due to:\n %s" % (pick.name, e) + reset)
		# validate ready
		if picking_ids:
			transfer_obj = self.env['stock.immediate.transfer']
			ready_pickings = picking_ids.filtered(lambda p: p.state == 'assigned' and not p.show_check_availability)
			if ready_pickings:
				# Bulk confirm to save time for ready pickings
				try:
					# transfer_obj.create({'pick_ids': ready_pickings}).process()
					return ready_pickings.button_validate()
				# results += "<li style='color:green'>%s is validated successfully</li>" \
				#            % ready_pickings.mapped('name')
				except Exception as e:
					results += "<li style='color:red'>%s picking not validate due to:\n %s</li>" % (ready_pickings.mapped('name'), e)
					_logger.error(red + "%s picking not validate due to:\n %s"
					              % (ready_pickings.mapped('name'), e) + reset)
			# Validate one by one remain
			for pick in picking_ids.filtered(lambda p: p.state != 'done'):
				try:
					transfer_obj.create({'pick_ids': pick}).process()
				except Exception as e:
					results += "<li style='color:red'>%s picking not validate due to:\n %s</li>" % (pick.name, e)
					_logger.error(red + "%s picking not validate due to:\n %s"
					              % (pick.name, e) + reset)
		else:
			results += "<li style='color:red'>No valid records found to use!!!</li>"
		results += "</ul>"
		message_id = self.env['bulk.message.wizard'].create({'message': _(results)})
		return {
			'name': _('Bulk Action Results'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'bulk.message.wizard',
			'res_id': message_id.id,
			'target': 'new'
		}
	
	def action_separate(self):
		"""
		Apply separation operations
		"""
		transfer_obj = self.env['stock.immediate.transfer']
		new_pickings = self.env['stock.picking']
		for picking in self:
			draft_pickings = picking.filtered(lambda p: p.state == 'draft')
			# Check if all picking location is internal
			# if picking.location_id.usage == 'internal' and picking.location_dest_id.usage == 'internal'
			if all(loc.usage == 'internal' for loc in [picking.location_id, picking.location_dest_id]):
				new_dest_location = picking.picking_type_id.separate_location_id
				separated_pick = picking._prepare_separated_picking(new_dest_location)
				separated_pick = self.create(separated_pick)
				if separated_pick:
					new_pickings += separated_pick
					# Mark As TO DO & try check Availability for new picking
					separated_pick.with_context(stop_auto_separate=True).action_confirm()
					separated_pick.action_assign()
					# Complete picking Work flow and assign new Destination
					picking.location_dest_id = new_dest_location.id
					picking.is_separated = True
					picking.separated_picking_id = separated_pick.id
					picking.move_ids_without_package.write({'location_dest_id': new_dest_location.id})
					picking.move_line_ids_without_package.write({'location_dest_id': new_dest_location.id})
					# Mark As TO DO: if there are any ready process
					if draft_pickings:
						draft_pickings.with_context(stop_auto_separate=True).action_confirm()
					# Check Availability if there are any waiting process
					waiting_pickings = picking.filtered(lambda p: p.state in ('waiting', 'confirmed'))
					if waiting_pickings:
						waiting_pickings.action_assign()
					# Validate: ready pickings
					ready_pickings = picking.filtered(lambda p: p.state == 'assigned')
					transfer_obj.create({'pick_ids': ready_pickings}).process()
		if self.env.context.get('auto_validate_new'):
			# TODO: call auto confirm action
			# self.with_context(active_ids=new_pickings).action_picking_bulk_validate()
			new_pickings.button_validate()
		return self.view_new_pickings(new_pickings.ids)
	
	def action_confirm(self):
		"""
		Auto Separate picking with MArk AS Todo action
		:return: Super
		"""
		if not self.env.context.get('stop_auto_separate'):
			for picking in self:
				if picking.allow_separate and not picking.is_separated:
					picking.action_separate()
		return super(StockPickingInherit, self).action_confirm()
	
	def action_bulk_separate(self):
		"""
		-Separate historical internal pickings
		- it should validate both pickings
		:return: new pickings views
		"""
		picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids')) \
			.filtered(lambda p: p.picking_type_id.code == 'internal' and p.location_id.usage == 'internal'
		                        and p.location_dest_id.usage == 'internal')
		return picking_ids.with_context(auto_validate_new=True).action_separate()
		
	def view_new_pickings(self, pick_ids):
		"""
		This function returns an action that display new created pickings
		"""
		action = self.env.ref('stock.action_picking_tree_all')
		result = action.read()[0]
		# choose the view_mode accordingly
		if not pick_ids or len(pick_ids) > 1:
			result['domain'] = "[('id','in',%s)]" % pick_ids
		elif len(pick_ids) == 1:
			res = self.env.ref('stock.view_picking_form', False)
			form_view = [(res and res.id or False, 'form')]
			if 'views' in result:
				result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
			else:
				result['views'] = form_view
			result['res_id'] = pick_ids[0]
		return result
	
	# --------------------------------------------------
	# Business methods
	# --------------------------------------------------
	
	@api.onchange('picking_type_id')
	def onchange_picking_type(self):
		res = super(StockPickingInherit, self).onchange_picking_type()
		if self.picking_type_id:
			self.allow_separate = self.picking_type_id.allow_separate
		return res
	
	def _prepare_separated_picking(self, src_location=False):
		return {
			# collect picking data
			'picking_type_id': self.picking_type_id.id,
			'partner_id': self.partner_id.id,
			'scheduled_date': self.scheduled_date,
			'date': self.scheduled_date,
			'origin': self.origin,
			'location_dest_id': self.location_dest_id and self.location_dest_id.id or False,
			'location_id': src_location and src_location.id or self.location_id.id,
			'company_id': self.company_id.id,
			'is_separated': True,
			'allow_separate': True,
			'separated_picking_id': self.id,
			'move_ids_without_package':
				[(0, 0, {
					# collect lines data
					'name': (line.name or '')[:2000],
					'product_id': line.product_id.id,
					'product_uom': line.product_uom.id,
					'product_uom_qty': line.product_uom_qty,
					'date': line.date,
					'date_deadline': line.date_deadline,
					'location_dest_id': line.location_dest_id and line.location_dest_id.id or False,
					'location_id': src_location and src_location.id or self.location_id.id,
					'partner_id': line.partner_id and line.partner_id.id or False,
					'state': 'draft',
					'company_id': line.company_id and line.company_id.id or False,
					'price_unit': line.price_unit,
					'picking_type_id': line.picking_type_id and line.picking_type_id.id or False,
					'group_id': line.group_id and line.group_id.id or False,
					'origin': line.origin,
					'warehouse_id': line.warehouse_id and line.warehouse_id.id or False,
				}) for line in self.move_ids_without_package]
		}

# Ahmed Salama Code End.
