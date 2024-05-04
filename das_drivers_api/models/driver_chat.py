from odoo import fields, models


class DriverChat(models.Model):
    _name = 'driver.chat'
    _description = 'driver.chat'

    name = fields.Many2one('sale.order', string="Sale Order")
    message = fields.Text('Message')
    images = fields.One2many('driver.chat.image', 'driver_chat_id', string="Images")
    image_found = fields.Boolean('Has Images')
    driver_user_id = fields.Many2one('res.users',string="Driver ",required=False)
    client_user_id = fields.Many2one('res.users',string="Client ",required=False)
    
    def show_image(self):
        for rec in self:
            image_ids = self.env['driver.chat.image'].sudo().search([('driver_chat_id', '=', rec.id)])

            return {
                'name': ('Show Images'),
                'view_mode': 'kanban',
                'view_id': rec.env.ref('das_drivers_api.show_images').id,
                'res_model': 'driver.chat.image',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('id', 'in', image_ids.ids)],
                'target': 'new'}