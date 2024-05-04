from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'
    _description = 'res.company'


    restaurant_loader_for_web_app = fields.Image(string='Restaurant Loader For Web App')
    loader_image_attachment = fields.Many2one('ir.attachment', compute="create_loader_attachment_image", store=True)

    splash_background_for_mobile_app = fields.Image(string='Splash Background For Mobile App')
    splash_image_attachment = fields.Many2one('ir.attachment', compute="create_splash_attachment_image", store=True)

    @api.depends('splash_background_for_mobile_app')
    def create_splash_attachment_image(self):
        for rec in self:
            if rec.splash_background_for_mobile_app:
                rec.splash_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img3",
                    'type': 'binary',
                    'datas': rec.splash_background_for_mobile_app,
                    'store_fname': str(rec.name) + "img3",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.splash_image_attachment = image_att.id

    @api.depends('restaurant_loader_for_web_app')
    def create_loader_attachment_image(self):
        for rec in self:
            if rec.restaurant_loader_for_web_app:
                rec.loader_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img2",
                    'type': 'binary',
                    'datas': rec.restaurant_loader_for_web_app,
                    'store_fname': str(rec.name) + "img2",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.loader_image_attachment = image_att.id