# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class StockLocationInherit(models.Model):
	_inherit = 'stock.location'
	
	return_src_location = fields.Boolean("Is Return Source Location?",
	                                     help="- Mark to use this location on source of return object")
	return_dest_location = fields.Boolean("Is Return Destination Location?",
	                                      help="- Mark to use this location on destination of return object")
# Ahmed Salama Code End.
