from odoo import fields, models, api


class SaleOrderLineImage(models.Model):
    _name = 'order.line.image'
    _description = 'Order Image'
    _inherit = ['image.mixin']

    sequence = fields.Integer(default=10, index=True)
    image = fields.Image(required=True)
    order_line_id = fields.Many2one('sale.order.line', "Order Line Images", index=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    images = fields.One2many('order.line.image', 'order_line_id', string="Images")
    image_found = fields.Boolean('Has Images')
    
    def show_image(self):


        for rec in self:
            image_ids = self.env['order.line.image'].sudo().search([('order_line_id','=',rec.id)])

            # return {
            #     'name':  ('Show Images'),
            #     'view_mode': 'tree',
            #     'view_id': rec.env.ref('das_event_sale_order.show_images').id,
            #     'res_model': 'order.line.image',
            #     'type': 'ir.actions.act_window',
            #     'nodestroy': True,
            #     'domain': [('id', 'in', image_ids.ids)],
            #     'target': 'new'}

            return {
                'name': ('Show Images'),
                'view_mode': 'kanban',
                'view_id': rec.env.ref('das_event_sale_order.show_images').id,
                'res_model': 'order.line.image',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('id', 'in', image_ids.ids)],
                'target': 'new'}