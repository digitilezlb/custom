from odoo import api, fields, models, _


class CouponProgram(models.Model):
    _inherit = 'coupon.program'

    image = fields.Image(string='Image')
    description = fields.Text(string='Description')


