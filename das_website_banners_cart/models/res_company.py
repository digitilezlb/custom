from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'


    cart_title = fields.Char(string="Cart Title", translate=True)
    cart_banner = fields.Image(string='Cart Banner')
    cart_image_attachment = fields.Many2one('ir.attachment', compute="create_cart_attachment_image", store=True)



    @api.depends('cart_banner')
    def create_cart_attachment_image(self):
        for rec in self:
            if rec.cart_banner:
                rec.cart_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.cart_title) + " img",
                    'type': 'binary',
                    'datas': rec.cart_banner,
                    'store_fname': str(rec.cart_title) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.cart_image_attachment = image_att.id