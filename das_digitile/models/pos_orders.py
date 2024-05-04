from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    """Inheriting the pos order model """
    _inherit = "pos.order"

    order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                               ("3", "Confirmed"),
                                               ("4", "In Progress"),
                                               ("5", "Ready"),
                                               ("6", "Out For Delivery"),
                                               ("7", "Delivered")
                                               ], store=True)


