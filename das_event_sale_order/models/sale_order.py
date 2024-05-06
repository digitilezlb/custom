from odoo import fields, models, api, _,exceptions
from datetime import datetime
from odoo.addons.das_publicfunction.controller.main import ProductInfo
from odoo.addons.das_user_notification.controller.main import Notification

class SaleOrder(models.Model):
    _inherit = "sale.order"
    event_type = fields.Char("Event Type")
