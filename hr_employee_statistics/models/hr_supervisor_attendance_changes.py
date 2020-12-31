# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HRSupervisorAttendanceLineInherit(models.Model):
	_inherit = 'hr.supervisor.attendance.line'
	
	statistics_line_id = fields.Many2one('hr.employee.statistics.line', "Statistics Line", ondelete='cascade')

# Ahmed Salama Code End.
