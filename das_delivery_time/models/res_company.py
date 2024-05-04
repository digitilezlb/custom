from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    time_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed'),
            # ('by_distance', 'By Distance'),
            ('by_zone', 'By Zone'),
        ],
        string="Time Type",
        default='fixed',
    )
    fixed_time = fields.Float(string="Fixed time", default=0)
    # has_delivery = fields.Boolean(string="Has Delivery",default=True)
    # has_pickup = fields.Boolean(string="Has Pickup")




