from odoo import fields, models, api


class DriverChatImage(models.Model):
    _name = 'driver.chat.image'
    _description = 'Driver Chat Image'
    _inherit = ['image.mixin']

    sequence = fields.Integer(default=10, index=True)
    image = fields.Image()
    driver_chat_id = fields.Many2one('driver.chat', "Driver. Chat Images", index=True)
    image_attachment = fields.Many2one('ir.attachment', compute="create_image_attachment",
                                                 store=True)

    @api.depends('image')
    def create_image_attachment(self):
        for rec in self:
            if rec.image:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.driver_chat_id.id) + " img",
                    'type': 'binary',
                    'datas': rec.image,
                    'store_fname': str(rec.driver_chat_id.id) + "img",
                    'res_model': 'driver.chat.image',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id

