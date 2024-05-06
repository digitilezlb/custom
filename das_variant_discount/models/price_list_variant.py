# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError


class PriceListVariant(models.Model):
    _name = "price.list.variant"
    _description = 'price.list.variant'
    _order = 'name'

    name = fields.Char(string='Name' )
    is_published = fields.Boolean('Published')
    detail_fields = fields.One2many('price.list.variant.detail', 'price_list_variant_id',
                                    string='Products', copy=True)
    company_id = fields.Many2one('res.company', string="company", required=False)

    @api.model
    def create(self, vals):
        data = vals
        product_list = []
        for item in data['detail_fields']:
            if isinstance(item[2], dict) and 'product_id' in item[2]:
                product_id = int(item[2]['product_id'])
                if product_id not in product_list:
                    product_list.append(product_id)
                else:
                    raise ValidationError(_("Product is already Exist"))

        for item in data['detail_fields']:
            if isinstance(item[2], dict) and 'discount' in item[2]:
                discount_value = float(item[2]['discount'])
                if discount_value > 100:
                    raise ValidationError(_("Percentage discount must be less than 100."))
                if discount_value < 0:
                    raise ValidationError(_("Percentage discount must be great than 0."))

        result = super(PriceListVariant, self).create(vals)
        return result

    def write(self, vals):

        data = vals
        product_list = []
        products = self.env['price.list.variant.detail'].sudo().search([('price_list_variant_id', '=', self.id)])
        for product in products:
            product_list.append(product.product_id.id)

        # try:
        if 'detail_fields' in data:
            for item in data['detail_fields']:
                if isinstance(item[2], dict) and 'product_id' in item[2]:
                    product_id = int(item[2]['product_id'])
                    if product_id not in product_list:
                        product_list.append(product_id)
                    else:
                        raise ValidationError(_("Product is already Exist"))

            for item in data['detail_fields']:
                if isinstance(item[2], dict) and 'discount' in item[2]:
                    discount_value = float(item[2]['discount'])

                    if discount_value > 100.0:
                        raise ValidationError(_("Percentage discount must be less than 100."))

                    if discount_value < 0.0:
                        raise ValidationError(_("Percentage discount must be great than 0."))
        # except:
        #     print('======error======error==========')
        #     pass
        res = super().write(vals)
        return res


class PriceListVariantDetail(models.Model):
    _name = 'price.list.variant.detail'
    _description = 'price.list.variant.detail'
    _order = 'id'

    price_list_variant_id = fields.Many2one('price.list.variant', string='price.list.variant', index=True,
                                            ondelete='cascade')
    product_id = fields.Many2one('product.product', string='product', index=True)
    discount = fields.Float(string='Discount (%)')
