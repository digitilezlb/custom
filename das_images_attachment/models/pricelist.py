from odoo import api, fields, models, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    image_attachment = fields.Many2one('ir.attachment', compute="create_attachment_image", store=True)

    @api.depends('image')
    def create_attachment_image(self):
        for rec in self:
            if rec.image:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'product.pricelist',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id
