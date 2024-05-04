from odoo import api, fields, models, _
from datetime import datetime, time
from odoo.exceptions import ValidationError

class AddZonePartner(models.Model):
    _inherit = 'res.partner'
    _description = 'inherit Contacts'

    is_default_address = fields.Boolean(string="Default Address", required=False)

