from odoo import api, fields, models, _
import string
from datetime import datetime, timedelta
import random


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # zone_id = fields.Many2one('zone.zone', string="Zone")
    city_id = fields.Many2one('state.city', string="City", domain="[('state_id', '=?', state_id)]")
    street_id = fields.Many2one('city.street', string="Street", domain="[('city_id', '=?', city_id)]")
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self._default_country())
    is_hidden = fields.Boolean()
    is_client = fields.Boolean(string="Client")

    def _default_country(self):
        lebanon = self.env['res.country'].search([('name', '=', 'Lebanon')])
        return lebanon

    # @api.onchange('zone_id')
    # def get_client_zone(self):
    #     for rec in self:
    #         if rec.zone_id:
    #             #         line = rec.env['zone.lines'].search([
    #             #             ('state', '=', rec.state_id.id),
    #             #             ('city', '=', rec.city_id.id), ('streets', '=', rec.street_id.id)
    #             #         ], limit=1)
    #             rec.marker_color = rec.zone_id.marker_color

    # @api.onchange('street_id')
    # def get_client_zone(self):
    #     for rec in self:
    #         if rec.street_id:
    #             line = rec.env['zone.lines'].search([('streets', '=', rec.street_id.id)])
    #             zone = line.zone_id
    #             rec.city_id = rec.street_id.city_id.id
    #             rec.state_id = rec.street_id.city_id.state_id.id
    #             rec.country_id = rec.street_id.city_id.state_id.country_id.id
    #             if rec.is_client == True:
    #                 # rec.zone_id = zone.id
    #                 rec.marker_color = zone.marker_color
