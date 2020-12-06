# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
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


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	def _action_done(self):
		"""
		Used to :
		- compute and store previous details
		"""
		res = super(StockPickingInherit, self)._action_done()
		_logger.info(green + "\n -----------------------------------------------------\n"
		             "Get historical qty and cost for %s" % len(self) + reset)
		for pick in self:
			# compute and store previous details
			pick.move_line_ids.execute_update_history()
			pick.date_done = pick.date
		return res
	
	@api.onchange('date')
	def _compute_scheduled_date(self):
		"""
		Replace core code with new one to depend on previous action date
		:return:
		"""
		for picking in self:
			picking.scheduled_date = picking.date
			picking.move_lines.write({
				'date': picking.date
			})
	
	def action_picking_bulk_validate(self):
		"""
		Add An action to validate multi records on stock pickings
		:return: view with confirmed pickings
		"""
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
					_logger.error(green + "%s is Mark as todo successfully" % pick.name + reset)
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
					_logger.error(green + "%s is check availability successfully" % pick.name + reset)
				
				except Exception as e:
					results += "<li style='color:red'>%s picking not check availability due to:<br/> %s</li>" % (
					pick.name, e)
					_logger.error(red + "%s picking not check availability due to:\n %s" % (pick.name, e) + reset)
		# validate ready
		if picking_ids:
			transfer_obj = self.env['stock.immediate.transfer']
			ready_pickings = picking_ids.filtered(lambda p: p.state == 'ready' and not p.show_check_availability)
			if ready_pickings:
				# Bulk confirm to save time for ready pickings
				try:
					transfer_obj.create({'pick_ids': ready_pickings}).process()
					results += "<li style='color:green'>%s is validated successfully</li>" \
					           % ready_pickings.mapped('name')
				except Exception as e:
					results += "<li style='color:red'>%s picking not validate due to:\n %s</li>" % (
					ready_pickings.mapped('name'), e)
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
		
# Ahmed Salama Code End.

