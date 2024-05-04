from odoo import api, fields, models
from datetime import date, datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_place_order = fields.Boolean(string="User place order", default=False,store=True)
