from odoo import fields, models, api


# class SaleOrderImage(models.Model):
#     _name = 'order.image'
#     _description = 'Order Image'
#     _inherit = ['image.mixin']
#
#     sequence = fields.Integer(default=10, index=True)
#     image = fields.Image(required=True)
#     order_id = fields.Many2one('sale.order', "Order Images", index=True)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # total_cbm = fields.Float('Total CBM', compute='get_total_cbm', store=True)
    # total_weight = fields.Float('Total Weight', compute='get_total_weight', store=True)
    # sugg_nb_boxes = fields.Integer('Suggested Boxes number', compute='get_total_number_of_boxes', store=True)
    # images = fields.One2many('order.image', 'order_id', string="Images")
    total_line = fields.Integer(string='Total Lines', compute="get_total_line", store=True)
    total_qty = fields.Float(string='Total Quantity', compute="get_total_qty", store=True)
    # zone_id = fields.Many2one('zone.zone', related="partner_id.zone_id", string='Zone')
    # is_confirmed = fields.Boolean(string="Retailer Agreement", default=False, readonly=True)

    @api.depends('order_line')
    def get_total_line(self):
        for rec in self:
            rec.total_line = len(self.order_line)

    @api.depends('order_line.product_uom_qty')
    def get_total_qty(self):
        for rec in self:
            rec.total_qty = sum(line.product_uom_qty for line in rec.order_line)

    # def action_confirm(self):
    #     result = super(SaleOrder, self).action_confirm()
    #     for rec in self:
    #         for line in rec.picking_ids.move_ids_without_package:
    #             for order_line in rec.order_line:
    #                 if line.product_id == order_line.product_id:
    #                     line.update({'unit_price': order_line.price_unit, 'tax_id': order_line.tax_id.id,
    #                                  'is_picked': order_line.is_picked})
    #         # for line in rec.picking_ids:
    #         #     line.sugg_nb_boxes = rec.sugg_nb_boxes
    #     return result

    # @api.depends('order_line.total_cbm')
    # def get_total_cbm(self):
    #     for rec in self:
    #         rec.total_cbm = sum(line.total_cbm for line in rec.order_line)

    # @api.depends('order_line.weight')
    # def get_total_weight(self):
    #     for rec in self:
    #         rec.total_weight = sum((line.weight * line.product_uom_qty) for line in rec.order_line)

    # @api.depends('total_cbm')
    # def get_total_number_of_boxes(self):
    #     for rec in self:
    #         if rec.env.ref("conf_parameters.nbr_of_boxes").value != 0:
    #             rec.sugg_nb_boxes = rec.total_cbm / rec.env.ref("conf_parameters.nbr_of_boxes").value
    #             if rec.sugg_nb_boxes < rec.total_cbm / rec.env.ref("conf_parameters.nbr_of_boxes").value:
    #                 rec.sugg_nb_boxes += 1
