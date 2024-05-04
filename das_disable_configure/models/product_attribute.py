from random import randint

from odoo import api, fields, models, tools, _, exceptions
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"


    def action_open_attribute_values(self):
        attribute = self.attribute_id
        if attribute.create_variant == 'no_variant':
            raise exceptions.UserError("You Can't configure 'Never' attribute.")
        return super(ProductTemplateAttributeLine, self).action_open_attribute_values()
