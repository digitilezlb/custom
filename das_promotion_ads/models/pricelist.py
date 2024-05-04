from odoo import api, fields, models, _
import json
from odoo import http
from odoo.http import request
import requests
from odoo.exceptions import ValidationError

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_published = fields.Boolean('Published')
    image = fields.Image(string='Image')
    is_promotion = fields.Boolean(default=False)
    is_banner = fields.Boolean(default=False)
    is_offer = fields.Boolean(default=False)

    # @api.model
    # def create(self, vals):
    #
    #
    #     if 'is_promotion' in vals:
    #         if vals['is_promotion']:
    #             raise ValidationError(_("The entered date of birthday is not acceptable !"))
    #
    #     return super(ProductPricelist, self).create(vals)

class ProductPricelistItems(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection(selection=lambda self: self._get_new_question_type(), string="Apply On",
                                  default='3_global', required=True, store=True,
                                  help='Pricelist Item applicable on selected option')
    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Discount'),
        ('formula', 'Formula')], index=True, default='percentage', required=True)


    @api.model
    def _get_new_question_type(self):

        selection = [
            ('3_global', 'All Products'),
            ('2_product_category', 'Product Category'),
            ('1_product', 'Product')]

        return selection

# @api.onchange('pricelist_id')
    # def get_price(self):
    #     self._get_new_question_type()
    #
    # @api.model
    # def _get_new_question_type(self):
    #     print('-------------self ------self--------self-------------')
    #     print('====================', self.pricelist_id.name)
    #     print('----------------------------------', self.pricelist_id.is_promotion)
    #     if self.pricelist_id.is_promotion:
    #         selection = [
    #             ('3_global', "All Products"),
    #             ('2_product_category', "Product Category"),
    #             ('1_product', "Product"),
    #         ]
    #         print('----------', selection)
    #     else:
    #         print('==========================================')
    #         selection = [('0_product_variant', "Product Variant")
    #                      ]
    #     return selection
