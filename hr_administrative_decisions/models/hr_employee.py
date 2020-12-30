from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    administrative_decisions_ids = fields.One2many('hr.administrative.decisions', 'employee_id')
    administrative_decisions_count = fields.Integer("Admin Decs Count", compute='_get_admin_desc')
    
    @api.onchange('administrative_decisions_ids')
    def _get_admin_desc(self):
        for emp in self:
            emp.administrative_decisions_count = len(emp.administrative_decisions_ids)
    
    def view_admin_desc(self):
        """
        This function returns an action that display new related administrative decisions
        """
        action = self.env.ref('hr_administrative_decisions.hr_administrative_decisions_action')
        result = action.read()[0]
        # choose the view_mode accordingly
        if not self.administrative_decisions_ids or len(self.administrative_decisions_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % self.administrative_decisions_ids.ids
        elif len(self.administrative_decisions_ids) == 1:
            res = self.env.ref('hr_administrative_decisions.hr_administrative_decisions_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = self.administrative_decisions_ids[0].id
        return result
