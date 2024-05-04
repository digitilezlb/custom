from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_bundle = fields.Boolean('Is Bundle')
