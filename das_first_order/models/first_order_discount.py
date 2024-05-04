from odoo import api, fields, models, tools, _, exceptions
from odoo.exceptions import UserError, ValidationError


class WebsiteFirstOrder(models.Model):
    _name = "website.first.order"
    _description = " Website first order discount"

    name = fields.Char(string='Name', required=True)
    discount_type = fields.Selection(
        [('1', '% Discount'),  ('2', 'Free Delivery')],
        string="Discount Type", required=True)
    # percentage_discount = fields.Float(string='Percentage')
    amount_discount = fields.Float(string='Discount', default=0)
    enable = fields.Boolean(string='Active', default = False)
    def write(self, vals):
        if 'discount_type' in vals:
            discount_type = int(vals['discount_type'])
        else:
            discount_type = int(self.discount_type)
        if discount_type == 1:
            if 'amount_discount' in vals:
                amount_discount = vals['amount_discount']
            else:
                amount_discount = self.amount_discount
        else:
            if 'amount_discount' in vals:
                amount_discount = vals['amount_discount']
            else:
                amount_discount = self.amount_discount
        if discount_type == 1:
            if amount_discount > 100:
                self.amount_discount = 0.0

                raise ValidationError(_("Percentage discount must be less than 100."))
            if amount_discount < 0:
                self.amount_discount = 0.0

                raise ValidationError(_("Percentage discount must be great than 0."))
        elif discount_type == 2:
            vals['amount_discount'] = 0.0
        res = super().write(vals)
        return res

    @api.model
    def create(self, vals):
        if 'discount_type' in vals:
            discount_type = int(vals['discount_type'])
        else:
            discount_type = int(self.discount_type)
        if discount_type == 1:
            if 'amount_discount' in vals:
                amount_discount = vals['amount_discount']
            else:
                amount_discount = self.amount_discount
        else:
            if 'amount_discount' in vals:
                amount_discount = vals['amount_discount']
            else:
                amount_discount = self.amount_discount
        if discount_type == 1:
            if amount_discount > 100:
                self.amount_discount = 0.0

                raise ValidationError(_("Percentage discount must be less than 100."))
            if amount_discount < 0:
                self.amount_discount = 0.0

                raise ValidationError(_("Percentage discount must be great than 0."))
        elif discount_type == 2:
            vals['amount_discount'] = 0.0
        result = super(WebsiteFirstOrder, self).create(vals)
        return result
