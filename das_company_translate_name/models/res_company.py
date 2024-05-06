import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_name_ar = fields.Char(string='Arabic Name')
    street_ar = fields.Char(string='Arabic Address')
    street2_ar = fields.Char(string='Arabic Street2')
