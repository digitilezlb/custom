import base64

from odoo import fields, models, api, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    image_attachment = fields.Many2one('ir.attachment', compute="create_attachment_image", store=True)

    @api.depends('category_image')
    def create_attachment_image(self):
        for rec in self:
            if rec.category_image:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.category_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'product.category',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id
