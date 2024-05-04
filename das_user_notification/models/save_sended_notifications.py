from odoo import fields, models, api
import json
from odoo import http
from odoo.http import request
import requests


class SentNotification(models.Model):
    _name = 'sent.notification'
    _description = 'save sent Notification Users'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Body', required=True)
    users = fields.Many2many('res.users', string='Receivers')
    sender = fields.Many2one('res.users', string='Sender')
    image = fields.Image(string='Image')
    image_attachment = fields.Many2one('ir.attachment', compute="create_image_attachment",
                                                 store=True)
    image_full_url = fields.Char(string='image_full_url' )
    # order_id = fields.Many2one('sale.order', string='Order')
    # picking_id = fields.Many2one('stock.picking', string='Picking')
    # batch_id = fields.Many2one('stock.picking.batch', string='Batch')
    notif_type = fields.Selection(
        [('order', 'Order'),
         ('announcement_1','Announcement'),
         ('promo', 'Promotions'),
         ('cat', 'Categories'),
         ('plat', 'Plat du Jour'),
         ('public', 'Public')
         ],
        string="Type")
    notif_type_id = fields.Integer(string="Id Of Notification Type")
    # promo_id = fields.Many2one('product.pricelist', string="promotions")
    # chat_id = fields.Many2one('users.chat')
    status = fields.Integer(default=1)


    @api.depends('image')
    def create_image_attachment(self):
        for rec in self:
            if rec.image:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'sent.notification',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id

