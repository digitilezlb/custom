from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    # order_status = fields.Selection(string="Order Status",
    #                                 selection=[("draft", "Draft"),
    #                                            ("confirmed", "Confirmed"),
    #                                            ("in_progress", "In Progress"),
    #                                            ("ready", "Ready"),
    #                                            ("out_for_delivery", "Out For Delivery"),
    #                                            ("delivered", "Delivered"),
    #                                            ("canceled", "Canceled")
    #                                            ],default='draft',
    #                                 help='To know the status of order')