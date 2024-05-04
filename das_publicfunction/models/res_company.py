# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    whatsapp = fields.Text('Whatsapp')
