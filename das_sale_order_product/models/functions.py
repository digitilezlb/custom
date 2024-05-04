from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class Thefunctions(models.Model):
    _name = "sale.order.product.thefunctions"

    # def get_product_product_details(self, product_product):
    #     product_variant_name = ''
    #     variant_attribute = []
    #     if product_product.product_template_variant_value_ids:
    #
    #         for variant in product_product.product_template_variant_value_ids:
    #             values_variant_attribute = {
    #                 "attribute_id": variant.attribute_id.id,
    #                 "attribute_name": variant.attribute_id.name,
    #                 "attribute_value_id": variant.id,
    #                 "attribute_value_name": variant.name
    #             }
    #             product_variant_name = variant.name + ':' + product_variant_name
    #             variant_attribute.append(values_variant_attribute)
    #
    #         if product_variant_name != '':
    #             product_variant_name = product_variant_name[:-1]
    #         else:
    #             product_variant_name = product_product.name
    #
    #     else:
    #         product_variant_name = product_product.name
    #     values_prod = {
    #         "product_product_id": product_product.id,
    #         "product_variant_name": product_variant_name,
    #         'variant_attribute_list': variant_attribute
    #     }
    #     return values_prod