# -*- coding: utf-8 -*-
from odoo import api, fields, models
import requests


class ResUserLog(models.Model):
    _inherit = 'res.users.log'
    
    location = fields.Char()
    dimension = fields.Char("Longitude,Latitude")
    login_date = fields.Datetime(
        compute="_get_login_date", string="Login Date")
    url = fields.Char(compute='get_location')
    
    # @api.multi
    def _get_login_date(self):
        for rec in self:
            rec.login_date = rec.create_date
            
    def get_location(self):
        default_location = "https://maps.google.com/maps?hl=en" \
                       "&ie=UTF8&z=12&iwloc=B&output=embed"
        if self.dimension:
            default_location += "&q=%s" % self.dimension
        self.url = default_location
        return default_location


class Users(models.Model):
    _inherit = 'res.users'
    
    @api.model
    def _update_last_login(self):
        vals = {}
        url = 'http://ipinfo.io/json'
        r = requests.get(url)
        js = r.json()
        dimension = js['loc']
        city = js['city']
        region = js['region']
        country_code = js['country']
        country_id = self.env['res.country'].search([('code', '=', country_code)], limit=1)
        address = "%s, %s, %s" % (city, region, country_id and country_id.name or country_code)
        vals.update({
            'location': address,
            'dimension': dimension,
            # 'user_id': self.env.user.id
        })
        user_log_id = self.env['res.users.log'].create(vals)
        user = self.env.user
        user.write({'log_ids': [(6, 0, [user_log_id.id])]})
