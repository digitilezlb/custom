# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # about_us = fields.Text('About Us')
    terms_and_conditions = fields.Text('Terms and Conditions', translate=True)
    privacy_policy = fields.Text('Privacy Policy', translate=True)
    support = fields.Text('Support', translate=True)

    # terms_and_conditions_url = fields.Char('Terms and Conditions URL')
    # privacy_policy_url = fields.Char('Privacy Policy URL')

    # logo_web_attachment = fields.Many2one('ir.attachment', compute="create_logo_web_attachment_image", store=True)

    # @api.depends('logo_web')
    # def create_logo_web_attachment_image(self):
    #     for rec in self:
    #         if rec.logo_web:
    #             rec.logo_web_attachment.unlink()
    #             image_att = rec.env['ir.attachment'].sudo().create({
    #                 'name': str(rec.name) + " img",
    #                 'type': 'binary',
    #                 'datas': rec.logo_web,
    #                 'store_fname': str(rec.name) + "img",
    #                 'res_model': 'res.company',
    #                 'res_id': rec.id,
    #                 'public': True
    #             })
    #             if image_att:
    #                 rec.logo_web_attachment = image_att.id
