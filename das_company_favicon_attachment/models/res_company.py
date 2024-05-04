# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    favicon_attachment = fields.Many2one('ir.attachment', compute="create_favicon_attachment_image", store=True)
    # #
    @api.depends('favicon')
    def create_favicon_attachment_image(self):
        for rec in self:
            if rec.favicon:
                rec.favicon_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img1",
                    'type': 'binary',
                    'datas': rec.favicon,
                    'store_fname': str(rec.name) + "img1",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.favicon_attachment = image_att.id



