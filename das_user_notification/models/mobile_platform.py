from odoo import api, fields, models, _


class MobilePlatform(models.Model):
    _name = 'mobile.platform'
    _description = 'mobile.platform'

    name = fields.Char()
