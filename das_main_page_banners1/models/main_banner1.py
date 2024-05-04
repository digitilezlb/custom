import base64
from odoo import api, fields, models


class MainBanner1(models.Model):
    _name = 'main.banner1'
    _description = 'main.banner1'

    name = fields.Char(string="Title", translate=True)
    description = fields.Char(string='Description', translate=True)
    banner_image = fields.Image(string='Banner Image')
    banner_image_attachment = fields.Many2one('ir.attachment', compute="create_banner_image_attachment", store=True)
    banner_url = fields.Char(string='URL')
    company_id = fields.Many2one('res.company', string="company", required=False)
    
    @api.depends('banner_image')
    def create_banner_image_attachment(self):
        for rec in self:
            if rec.banner_image:
                rec.banner_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.banner_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'website.banner',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.banner_image_attachment = image_att.id
