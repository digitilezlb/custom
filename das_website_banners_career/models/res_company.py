from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'


    career_banner = fields.Image(string='Career Banner')
    career_banner_attachment = fields.Many2one('ir.attachment',
                                             compute="create_career_banner_attachment_image",
                                             store=True)



    @api.depends('career_banner')
    def create_career_banner_attachment_image(self):
        for rec in self:
            if rec.career_banner:
                rec.career_banner_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.career_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.career_banner_attachment = image_att.id

