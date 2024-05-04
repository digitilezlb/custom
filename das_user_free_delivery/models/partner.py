from odoo import api, fields, models, _
import string
from datetime import datetime, timedelta
import random


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'res.partner'


    free_delivery = fields.Boolean(string="Free Delivery")