# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    picking_bulk_validate = fields.Boolean("Picking Bulk Validate",
                                           help="When Activate this action, system will add bulk action to validate"
                                                " multi pickings on same time.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['picking_bulk_validate'] = self.env['ir.config_parameter'].sudo().get_param(
            'product_card_report.picking_bulk_validate')
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('product_card_report.picking_bulk_validate',
                                                         self.picking_bulk_validate)
        # Active/Disable server action according to settings
        action_id = self.env.ref('product_card_report.server_action_picking_bulk_validate')
        if self.picking_bulk_validate and not action_id.binding_model_id:
            action_id.create_action()
        elif not self.picking_bulk_validate and action_id.binding_model_id:
            action_id.unlink_action()
        

