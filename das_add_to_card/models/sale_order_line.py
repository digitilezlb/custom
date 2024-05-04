from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    """Inheriting the pos order model """
    _inherit = "sale.order.line"

    combo_content = fields.Json(string="combo content")
