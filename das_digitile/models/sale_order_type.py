from odoo import fields, models


class SaleOrderType(models.Model):
    _name = 'sale.order.type'

    name = fields.Char(string='name')
