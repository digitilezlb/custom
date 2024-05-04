
from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'zone.zone'
    delivery_fees = fields.Float(string="Delivery Fees", default=0)
    show_fee = fields.Boolean(compute="show_delivery_fees")
    @api.depends('company_id')
    def show_delivery_fees(self):
        try:
            for rec in self:
                if rec.company_id.fees_type:

                    if rec.company_id.fees_type == 'by_zone':
                        rec.show_fee = True
                    else:
                        rec.show_fee = False
                else:
                    rec.show_fee = False
        except:
            rec.show_fee = False