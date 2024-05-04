# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'


    terms_and_conditions_url = fields.Char('Terms and Conditions URL')
    privacy_policy_url = fields.Char('Privacy Policy URL')


