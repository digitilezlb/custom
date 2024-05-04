from odoo import fields, models


class ContactUs(models.Model):
    _name = 'contact.us'
    _description = 'contact us'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    comment = fields.Text(string='Comment')
    company_id = fields.Many2one('res.company', string="company", required=False)