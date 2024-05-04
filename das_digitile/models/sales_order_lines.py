from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    """Inheriting the pos order model """
    _inherit = "sale.order.line"
    notes = fields.Text(string="Notes")
    note_addons = fields.Text(string="Notes Add Ons")
    notes_removable_ingredients = fields.Text(string="Notes Removable Ingredients")
    addons_note = fields.Json(string="Addons")
    removable_ingredients_note = fields.Json(string="Removable Ingredients")
    order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                               ("3", "Confirmed"), 
                                               ("4", "In Progress"),
                                               ("5", "Ready")
                                               ], default="2", help='To know the status of order', store=True)

    from_which_group = fields.Integer(default=0)
    #this field is used to know from wich group the user buy the item.
    # 0 => normal
    # 1 => from drinks
    # 2 => from sides
    # 3 => from desserts
    # 4 => from related products
    # 5 => from liked products