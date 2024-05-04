from odoo import _, api, fields, models, tools, Command


class PlacesReplenishment(models.TransientModel):
    _name = "places.replenishment"
    _description = "Places Replenishment"

    location_id = fields.Many2one('stock.location', domain=[('type', '=', 'unite_of_stock')])
    products = fields.One2many('location.storage', 'location_id', related="location_id.location_storage",
                               string="Location Storage", readonly=False)

    def add_product_quantity(self):
        for rec in self:
            for i in rec.products:
                i.actual_quantity = i.actual_quantity + i.added_quantity
                i.added_quantity = 0


