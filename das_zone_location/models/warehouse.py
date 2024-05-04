from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    zone_ids = fields.One2many('zone.zone', 'warehouse_id', string="Zone")
