import base64
from odoo import api, fields, models


class DasCaption(models.Model):
    _name = 'das.caption'
    _description = 'das.caption'
    name = fields.Char(string='', default='')
    drinks_caption = fields.Char(string='Drinks Caption', default='Drinks', required=True, translate=True)
    sides_caption = fields.Char(string='Sides Caption', default='Sides', required=True, translate=True)
    related_caption = fields.Char(string='Related Caption', default='Related', required=True, translate=True)
    liked_caption = fields.Char(string='Liked Caption', default='Liked', required=True, translate=True)
    desserts_caption = fields.Char(string='Desserts Caption', default='Desserts', required=True, translate=True)

