from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    is_log_in = fields.Boolean(string="Log In",default = False)
    log_time = fields.Datetime()

