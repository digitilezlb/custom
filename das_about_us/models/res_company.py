# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'


    about_us_banner = fields.Image(string='About Us Banner')
    about_us_banner_attachment = fields.Many2one('ir.attachment', compute="create_about_us_banner_attachment_image", store=True)

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

    who_we_are_title = fields.Char(string="Title", translate=True)
    who_we_are_description = fields.Char(string="Description", translate=True)

    vision_title = fields.Char(string="Title", translate=True)
    vision_description = fields.Char(string="Description", translate=True)

    mission_title = fields.Char(string="Title", translate=True)
    mission_description = fields.Char(string="Description", translate=True)

    story_title = fields.Char(string="Title", translate=True)
    story_description = fields.Char(string="Description", translate=True)

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
                    'res_model': 'res.company',
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
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_link_attachment = image_att.id