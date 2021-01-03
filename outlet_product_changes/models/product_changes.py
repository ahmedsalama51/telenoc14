# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->
YEAR = 2015  # replace 2000 with your a start year
YEAR_LIST = []
while YEAR != 2050:  # replace 2100 with your end year
	YEAR_LIST.append((str(YEAR), str(YEAR)))
	YEAR += 1


class ProductColor(models.Model):
	_name = 'product.color'
	_description = "Product Color"
	
	name = fields.Char("Color", required=True, translate=True)
	code = fields.Char("Code")


class ProductBrand(models.Model):
	_name = 'product.brand'
	_description = "Product Brand"
	
	name = fields.Char("Brand", required=True)
	code = fields.Char("Code")
	

class ProductDepartment(models.Model):
	_name = 'product.department'
	_description = "Product Department"
	
	name = fields.Char("Department", required=True)
	code = fields.Char("Code")
	

class ProductSeason(models.Model):
	_name = 'product.season'
	_description = "Product Season"
	
	name = fields.Char("Season", required=True)
	code = fields.Char("Code")
	

class ProductGroup(models.Model):
	_name = 'product.group'
	_description = "Product Group"
	
	name = fields.Char("Group", required=True)
	code = fields.Char("Code")
	

class ProductTemplateInherit(models.Model):
	_inherit = 'product.template'
	
	oe_vendor_id = fields.Many2one('res.partner', "Vendor", domain=[('supplier_rank', '!=', 0)])
	oe_Country_id = fields.Many2one('res.country', "Country")
	oe_year = fields.Selection(YEAR_LIST, "Year", default=str(fields.Date.today().year))
	
	oe_color_id = fields.Many2one('product.color', "Color")
	oe_brand_id = fields.Many2one('product.brand', "Brand")
	oe_department_id = fields.Many2one('product.department', "Department")
	oe_season_id = fields.Many2one('product.season', "Season")
	oe_group_id = fields.Many2one('product.group', "Group")
	

# Ahmed Salama Code End.
