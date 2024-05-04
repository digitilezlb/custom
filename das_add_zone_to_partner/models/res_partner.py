from odoo import api, fields, models, _
from datetime import datetime, time
from odoo.exceptions import ValidationError

class AddZonePartner(models.Model):
    _inherit = 'res.partner'
    _description = 'inherit Contacts'

    zone_id = fields.Many2one('zone.zone', string="zone", required=False, readonly=True)

