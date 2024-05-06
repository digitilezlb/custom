# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WebsiteFAQ(models.Model):
    _name = 'website.faq'
    _description = 'Website FAQ'

    name = fields.Text(string="Question", translate=True)
    answer = fields.Text(string="Answer", translate=True)
    banner = fields.Image(string="Image")
    banner_attachment = fields.Many2one('ir.attachment', compute="create_banner_attachment", store=True)
    company_id = fields.Many2one('res.company', string="company", required=False)

    @api.depends('banner')
    def create_banner_attachment(self):
        for rec in self:
            if rec.banner:
                rec.banner_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'website.faq',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.banner_attachment = image_att.id