from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    fees_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed'),
            # ('by_distance', 'By Distance'),
            ('by_zone', 'By Zone'),
        ],
        string="Fees Type",
        default='fixed',
    )
    fixed_fees = fields.Float(string="Fixed Fees", default=0)
    # minimum_fees = fields.Float(string="Minnimum Fees", default=0)
    # price_by_km = fields.Float(string="Price By Km", default=0)