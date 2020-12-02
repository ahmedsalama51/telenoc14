# -*- coding: utf-8 -*-
from odoo import models, fields, api


# Ahmed Salama Code Start ---->

class ProductCardReportWizardStates(models.Model):
    _name = 'product.card.report.wizard.states'
    _description = "Product Card Wizard States"
    
    name = fields.Char("State")
    value = fields.Char("Value")


class ProductCardReportWizard(models.TransientModel):
    _name = 'product.card.report.wizard'
    
    # TODO: This to be used on the future using M2M fields to give more future
    # TODO: ADD state field as selection field to be filtered with
    product_id = fields.Many2one(comodel_name='product.product', string="Product", required=True)
    location_ids = fields.Many2many(comodel_name='stock.location', string="Location", required=True,
                                    domain=[('usage', '=', 'internal')])
    state_ids = fields.Many2many(comodel_name='product.card.report.wizard.states', string="States",
                                 relation='product_card_report_wizard_states_rel')
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    @api.model
    def default_get(self, field_list):
        result = super(ProductCardReportWizard, self).default_get(field_list)
        result['state_ids'] = [(6, 0, self.env.ref('product_card_report.report_product_card_state_done').ids)]
        return result
    
    def print_report(self):
        """
        Print Report with data of filters
        :return:
        """
        
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['date_from', 'date_to', 'location_ids', 'product_id'])
        if self.state_ids:
            states = self.state_ids
        else:
            states = self.env['product.card.report.wizard.states'].search([])
        res[0]['states'] = states.mapped('name')
        res[0]['states_value'] = states.mapped('value')
        res = res and res[0] or {}
        datas['form'] = res
        return self.env.ref('product_card_report.report_product_card').report_action([], data=datas)


# Ahmed Salama Code End.
