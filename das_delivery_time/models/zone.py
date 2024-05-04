
from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'zone.zone'

    delivery_time = fields.Float(string="Delivery Time (min)", default=0)
    show_time = fields.Boolean(compute="show_delivery_time")

    @api.depends('company_id')
    def show_delivery_time(self):
        try:
            for rec in self:

                if rec.company_id.time_type:
                    if rec.company_id.time_type == 'by_zone':
                        rec.show_time = True
                    else:
                        rec.show_time = False
                else:
                    rec.show_time = False
        except:
            rec.show_time = False