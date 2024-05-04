from odoo import api, fields, models, exceptions
import time

class AboutUs(models.Model):
    _name = "about.us"
    _description = "about.us"

    name = fields.Char(string='Name',required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    about_us_banner = fields.Image(string="Banner")
    about_us_banner_attachment = fields.Many2one('ir.attachment', compute="create_about_us_banner_attachment_image",
                                                 store=True)

    links = fields.Selection(
        selection=[
            ('video', 'Video'),
            ('image', 'Image'),
        ],
        string="Links",
        default='image',
    )
    video_url = fields.Char(string="Video Url")
    image_link = fields.Image(string="Image")
    image_link_attachment = fields.Many2one('ir.attachment', compute="create_image_link_attachment_image", store=True)

    company_id = fields.Many2one('res.company', string="company", required=False)

    @api.depends('about_us_banner')
    def create_about_us_banner_attachment_image(self):
        for rec in self:
            if rec.about_us_banner:
                rec.about_us_banner_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.about_us_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'about.us',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:

                    rec.about_us_banner_attachment = image_att.id



    @api.depends('image_link')
    def create_image_link_attachment_image(self):
        for rec in self:
            if rec.image_link:
                rec.image_link_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + "2 img",
                    'type': 'binary',
                    'datas': rec.image_link,
                    'store_fname': str(rec.name) + "2img",
                    'res_model': 'about.us',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_link_attachment = image_att.id

    # @api.model
    # def create(self, vals):
    #     existing_record = self.search([])
    #     if existing_record:
    #         raise exceptions.UserError("Only one 'About Us' record is allowed.")
    #     return super(AboutUs, self).create(vals)