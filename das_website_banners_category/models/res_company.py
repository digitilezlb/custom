from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'

    category_title = fields.Char(string="Category Title", translate=True)
    category_banner = fields.Image(string='Category Banner')
    category_image_attachment = fields.Many2one('ir.attachment', compute="create_category_attachment_image", store=True)



    @api.depends('category_banner')
    def create_category_attachment_image(self):
        for rec in self:
            if rec.category_banner:
                rec.category_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.category_title) + " img",
                    'type': 'binary',
                    'datas': rec.category_banner,
                    'store_fname': str(rec.category_title) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.category_image_attachment = image_att.id

