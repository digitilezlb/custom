from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """Inheriting the pos order model """
    _inherit = "sale.order"

    # order_status = fields.Selection(string="Order Status",
    #                                 selection=[("draft", "Draft"),
    #                                           ("confirmed", "Confirmed"),
    #                                           ("in_progress", "In Progress"),
    #                                           ("ready", "Ready"),
    #                                           ("out_for_delivery", "Out For Delivery"),
    #                                           ("delivered", "Delivered")
    #                                           ],
    #                                 help='To know the status of order')
    
    order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                               ("3", "Confirmed"),
                                               ("4", "In Progress"),
                                               ("5", "Ready"),
                                               ("6", "Out For Delivery"),
                                               ("7", "Delivered")
                                               ],default="2", help = 'To know the status of order', store = True, compute = "change_order_status",
                                    readonly = False)
                                    
    delivery_date = fields.Datetime(
        string="Delivery Date",
        required=False,
        help="Creation date of delivery orders.") #,
        #default=fields.Datetime.now)#

    # sale_order_type_id = fields.Many2one('sale.order.type', string="Order Type", required=True)
    sale_order_type = fields.Selection(string="Order Type",
                                    selection=[("1", "Delivery"),
                                               ("2", "Pick Up"),
                                               ("3", "Event"),
                                               ], default="1", help='To know the type of order', store=True,
                                    readonly=False)
                                    
    call_function = fields.Boolean(compute='confirm_sale_order', store=True)
    # company_id = fields.Many2one('res.company', string="Company", required=True)
    
    @api.depends('state')
    def change_order_status(self):
        for rec in self:
            if rec.state == 'sale':
                rec.order_status = "3"



    @api.depends('order_status')
    def confirm_sale_order(self):
        for rec in self:
            if rec.order_status == '3' and rec.state == 'draft':
                rec.action_confirm()