from odoo import fields, models


class DriverOrderLocationData(models.Model):
    _name = 'driver.order.location.data'
    _description = 'driver.order.location.data'

    driver_id = fields.Many2one('res.partner', string="Driver")
    order_id = fields.Many2one('sale.order', string="Sale Order")
    latitude = fields.Float(string="Latitude", digits=(16, 4))
    longitude = fields.Float(string="Longitude", digits=(16, 4))
    location = fields.Char('Location')


class SaleOrder(models.Model):
    _inherit ="sale.order"

    payment_status = fields.Char('Payment Status')

