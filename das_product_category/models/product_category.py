from odoo import fields, models, api, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_grocery = fields.Boolean('Grocery Category')
    is_main = fields.Boolean('Is Main Category')
    category_image = fields.Binary('Category Image')
    name_ar = fields.Char(string="Arabic name", required=True)
    is_publish = fields.Boolean('Publish')

    # def set_as_grocery_category(self):
    #     for rec in self:
    #         all_categories = rec.env['product.category'].sudo().search([])
    #         for category in all_categories:
    #             category.is_grocery = False
    #         rec.is_grocery = True
