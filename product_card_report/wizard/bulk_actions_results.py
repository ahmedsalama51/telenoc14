# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class MessageWizard(models.TransientModel):
    _name = 'bulk.message.wizard'

    message = fields.Html('Message', readonly=True)

    def action_close(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

# Ahmed Salama Code End.]
