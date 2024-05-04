from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # weight = fields.Float(related="product_id.weight", string="Weight")
    # volume = fields.Float(string="CBM", compute="get_cbm", store=True)
    # product_location = fields.Many2one('stock.location', related="product_id.location_shelf", string="Location")
    # is_picked = fields.Boolean(string="Picked")
    # total_cbm = fields.Float(string='Total CBM', compute="get_total_cbm")

    # @api.depends('product_id')
    # def get_cbm(self):
    #     for rec in self:
    #         rec.volume = rec.product_id.length * rec.product_id.breadth * rec.product_id.height

    # @api.depends('volume', 'product_uom_qty')
    # def get_total_cbm(self):
    #     for rec in self:
    #         rec.total_cbm = rec.volume * rec.product_uom_qty

    @api.onchange('product_id')
    def get_discount(self):
        for rec in self:
            rec.discount = rec.product_id.product_tmpl_id.discount
