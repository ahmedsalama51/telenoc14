from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_requests_ids = fields.One2many('hr.employee.request', 'employee_id')
    employee_requests_count = fields.Integer("Admin Decs Count", compute='_get_employee_requests')
    
    @api.onchange('employee_requests_ids')
    def _get_employee_requests(self):
        for emp in self:
            emp.employee_requests_count = len(emp.employee_requests_ids)
    
    def view_employee_requests(self):
        """
        This function returns an action that display new related Employee Requests
        """
        action = self.env.ref('hr_employee_requests.hr_hr_employee_request_action')
        result = action.read()[0]
        # choose the view_mode accordingly
        if not self.employee_requests_ids or len(self.employee_requests_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % self.employee_requests_ids.ids
        elif len(self.employee_requests_ids) == 1:
            res = self.env.ref('hr_employee_requests.hr_hr_employee_request_form_view', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = self.employee_requests_ids[0].id
        return result
