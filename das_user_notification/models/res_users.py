from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    user_token = fields.Text(string="Token", store=True)
    user_platform = fields.Many2one('mobile.platform')
