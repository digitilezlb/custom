from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'
    _description = 'res.company'


    url_play_store = fields.Char(string='Play Store URL')
    url_app_store = fields.Char(string='App Store URL')


