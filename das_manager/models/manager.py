from odoo import api, fields, models, _
from datetime import datetime, time




class Manager(models.Model):
    _inherit = 'res.partner'
    _description = 'inherit Contacts'

    is_manager = fields.Boolean(string='Is Manager', default=False)



