import base64
from odoo import api, fields, models


class CareerInformation(models.Model):
    _name = 'career.information'
    _description = 'career.information'

    name = fields.Char(string='Name', required=True, translate=True)
    title = fields.Char(string='Title', required=True, translate=True)
    description = fields.Char(string='Description', required=True, translate=True)
    icon1 = fields.Image(string='Icon 1')
    icon1_attachment = fields.Many2one('ir.attachment', compute="create_attachment_icon1", store=True)
    icon2 = fields.Image(string='Icon 2')
    icon2_attachment = fields.Many2one('ir.attachment', compute="create_attachment_icon2", store=True)
    icon3 = fields.Image(string='Icon 3')
    icon3_attachment = fields.Many2one('ir.attachment', compute="create_attachment_icon3", store=True)
    title1 = fields.Char('Title 1', translate=True)
    title2 = fields.Char('Title 2', translate=True)
    title3 = fields.Char('Title 3', translate=True)
    description1 = fields.Char(string='Description 1', translate=True)
    description2 = fields.Char(string='Description 2', translate=True)
    description3 = fields.Char(string='Description 3', translate=True)
    vacancies_title = fields.Char(string='Vacancies title', required=True, translate=True)
    vacancies_description = fields.Char(string='Vacancies description', required=True, translate=True)
    company_id = fields.Many2one('res.company', string="Company", required=False)
    
    @api.depends('icon1')
    def create_attachment_icon1(self):
        for rec in self:
            if rec.icon1:
                rec.icon1_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.icon1,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'services.solutions',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.icon1_attachment = image_att.id

    @api.depends('icon2')
    def create_attachment_icon2(self):
        for rec in self:
            if rec.icon2:
                rec.icon2_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.icon2,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'services.solutions',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.icon2_attachment = image_att.id

    @api.depends('icon3')
    def create_attachment_icon3(self):
        for rec in self:
            if rec.icon3:
                rec.icon3_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.icon3,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'services.solutions',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.icon3_attachment = image_att.id
