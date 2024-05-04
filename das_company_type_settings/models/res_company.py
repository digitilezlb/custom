from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'


    has_delivery = fields.Boolean(string="Has Delivery",default=True)
    has_pickup = fields.Boolean(string="Has Pickup")




