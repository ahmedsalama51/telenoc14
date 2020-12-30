# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AdministrativeDecisionsType(models.Model):
    _name = 'administrative.decisions.type'
    _description = 'Administrative Decisions Type'
    
    name = fields.Char(required=1)
    payroll_type = fields.Selection([('none', 'Not Effect'),
                                     ('appraisal', 'Appraisal(+)'),
                                     ('payslip_increase', 'Payslip(+)'),
                                     ('payslip_decrease', 'Payslip(-)')], "Payroll Effect", required=True,
                                    default='none', help="Assign Affection on payroll equations such as:\n"
                                                         "- None: Wont effect on payroll at all.\n"
                                                         "- Appraisal(+): effect on wage increasing as annual appraisal \n"
                                                         "- Payslip(+): effect on payslip increasing\n"
                                                         "- Payslip(-): effect on payslip decreasing\n")


class HrAdministrativeDecisions(models.Model):
    _name = 'hr.administrative.decisions'
    _description = 'Administrative Decisions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    
    name = fields.Char("Decision", readonly=1)
    active = fields.Boolean("Active", default=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
                                 index=True, required=True, readonly=1,
                                 states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  track_visibility='onchange')
    decision_type_id = fields.Many2one('administrative.decisions.type', required=True,
                                       string='Type Of Decision')
    payroll_type = fields.Selection(related='decision_type_id.payroll_type')
    amount = fields.Float("Amount")
    date = fields.Date(string="Date")
    description = fields.Text(string="Description")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approve', 'First Approve'),
        ('second_approve', 'Second Approve')
    ], string='Status', readonly=True, tracking=True, copy=False, default='draft')

    # --------------------------------------------------
    # CRUD
    # --------------------------------------------------
    @api.model
    def create(self, vals):
        """
		Add Seq for Receive
		:param vals: create vals
		:return: SUPER
		"""
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.administrative.decisions.code')
        return super(HrAdministrativeDecisions, self).create(vals)

    def action_draft(self):
        self.state = "draft"
    
    def action_first_approve(self):
        self.state = "first_approve"
    
    def action_second_approve(self):
        self.state = "second_approve"
    
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('You Can Not Delete a Record Which Is Not Draft.'))
            res = super(HrAdministrativeDecisions, record).unlink()
            return res
