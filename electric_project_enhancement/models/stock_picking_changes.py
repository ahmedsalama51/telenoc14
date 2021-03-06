# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
# Ahmed Salama Code Start ---->


class StockPickingTypeInherit(models.Model):
	_inherit = 'stock.picking.type'
	
	employee_mandatory = fields.Boolean("Employee Show and Required")
	
	
class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	employee_id = fields.Many2one('hr.employee', "Employee")
	employee_mandatory = fields.Boolean(related='picking_type_id.employee_mandatory')
	task_id = fields.Many2one('project.task', 'Task')
	
	@api.onchange('task_id')
	def change_lines_task(self):
		for picking in self:
			if picking.task_id:
				for line in picking.move_lines:
					line.task_id = picking.task_id
		
# Ahmed Salama Code End.

