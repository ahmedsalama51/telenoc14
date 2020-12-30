from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    supervisor_attendance_ids = fields.One2many('hr.supervisor.attendance', 'employee_id')
    supervisor_attendance_count = fields.Integer("Admin Decs Count", compute='_get_supervisor_attendance')
    
    @api.onchange('supervisor_attendance_ids')
    def _get_supervisor_attendance(self):
        for emp in self:
            emp.supervisor_attendance_count = len(emp.supervisor_attendance_ids)
    
    def view_supervisor_attendance(self):
        """
        This function returns an action that display new related Employee Requests
        """
        action = self.env.ref('hr_supervisor_attendance.hr_supervisor_attendance_action')
        result = action.read()[0]
        # choose the view_mode accordingly
        if not self.supervisor_attendance_ids or len(self.supervisor_attendance_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % self.supervisor_attendance_ids.ids
        elif len(self.supervisor_attendance_ids) == 1:
            res = self.env.ref('hr_supervisor_attendance.hr_supervisor_attendance_form_view', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = self.supervisor_attendance_ids[0].id
        return result
