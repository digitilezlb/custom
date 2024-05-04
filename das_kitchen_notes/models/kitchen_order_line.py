from odoo import api, fields, models
from odoo.exceptions import ValidationError




class DigitileOrderkitchenLine(models.Model):

    _inherit = "digitile.order.kitchen.line"
    kitchen_notes = fields.Text(string="Kitchen Notes",translate=True)