from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    image_attachment = fields.Many2one('ir.attachment', compute="create_attachment_image", store=True)

    @api.depends('image_1920')
    def create_attachment_image(self):
        for rec in self:
            if rec.image_1920:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.image_1920,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'product.template',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id


class ProductImage(models.Model):
    _inherit = 'product.image'

    image_attachment = fields.Many2one('ir.attachment', compute="create_attachment_image", store=True)

    @api.depends('image_1920')
    def create_attachment_image(self):
        for rec in self:
            if rec.image_1920:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.product_tmpl_id.name) + " img",
                    'type': 'binary',
                    'datas': rec.image_1920,
                    'store_fname': str(rec.product_tmpl_id.name) + "img",
                    'res_model': 'product.image',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id
