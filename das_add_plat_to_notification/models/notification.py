from odoo import fields, models, api



class NotificationNotification(models.Model):
    _inherit = 'notification.notification'

    notification_type = fields.Selection(
        [('public', 'Public'), ('promo', 'Promotion'), ('cat', 'Category'), ('plat', 'Plat du Jour')],
        string="Notification Type")