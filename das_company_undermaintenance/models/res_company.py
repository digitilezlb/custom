from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'
    _description = 'res.company'

    disable_users = fields.Boolean(string='Disable Users',default=False)
    maintenance_mode = fields.Boolean(string='Maintenance Mode',default=False)


