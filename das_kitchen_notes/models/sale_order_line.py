from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"
    kitchen_notes = fields.Text(string="Kitchen Notes",translate=True)


