from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosOrderLine(models.Model):
    """Inheriting the pos order model """
    _inherit = "pos.order.line"


   order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                                ("3", "Confirmed"), 
                                               ("4", "In Progress"),
                                               ("5", "Ready")
                                               ], default="2", help='To know the status of order', store=True)
