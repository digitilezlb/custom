from odoo import api, fields, models

class AboutUsSlider(models.Model):
    _name = "about.us.slider"
    _description = "about.us.slider"

    name = fields.Char(string='Name', translate=True)

    about_us_slider_image = fields.Image(string="Image")
    about_us_slider_image_attachment = fields.Many2one('ir.attachment', compute="create_about_us_slider_image_attachment_image",
                                                 store=True)
    company_id = fields.Many2one('res.company', string="company", required=False)

    @api.depends('about_us_slider_image')
    def create_about_us_slider_image_attachment_image(self):
        for rec in self:
            if rec.about_us_slider_image:
                rec.about_us_slider_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.about_us_slider_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'about.us',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.about_us_slider_image_attachment = image_att.id