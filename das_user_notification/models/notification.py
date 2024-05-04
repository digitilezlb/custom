from odoo import fields, models, api, exceptions
import json
from odoo import http
from odoo.http import request
import requests
from datetime import date, datetime
from odoo.addons.das_user_notification.controller.main import Notification

class NotificationNotification(models.Model):
    _name = 'notification.notification'
    _description = 'Notification Users'

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string='Description', required=True)
    image = fields.Image(string='Image')
    # retailers = fields.Many2many('res.users', string='Retailers')
    is_send = fields.Boolean()
    current_date = fields.Date(string="Send Date", readonly=True)
    image_attachment = fields.Many2one('ir.attachment', compute="create_image_attachment",
                                       store=True)
    customer_type = fields.Selection(
        [('1', 'All Customers'), ('2', 'Customers'), ('3', 'Products'),('4', 'Zones')],
        string="Customer Type", default='1')

    customers = fields.Many2many('res.partner', string='Customers',domain=lambda self: self._get_domain_for_custom_field())
    products = fields.Many2many('product.template', domain=[('is_delivery', '=', False)], string='Products')
    zones = fields.Many2many('zone.zone', string='Zones')

    notification_type = fields.Selection(
        [('public', 'Public'), ('promo', 'Promotion'), ('cat', 'Category')],
        string="Notification Type")

    promotion = fields.Many2one('product.pricelist', domain=[('is_promotion', '=', True)], string='Promotion')
    category = fields.Many2one('product.category', string='Category')
    platdejour = fields.Many2one('plat.de.jour', string='Plat Du Jour')

    def _get_domain_for_custom_field(self):
        partners = self.env['res.partner'].sudo().search([('is_client', '=', True)])
        all_partners = []
        final_partners = []
        partner_id = 0

        for partner in partners:
            if partner.parent_id:
                if partner.parent_id.is_client:
                    partner_id = partner.parent_id.id

            else:
                partner_id = partner.id
            if partner_id!=0 and partner_id not in all_partners:
                all_partners.append(partner_id)

        users = self.env['res.users'].sudo().search([('partner_id', 'in', all_partners)])
        for user in users:
            if user.user_token:
                final_partners.append(user.partner_id.id)

        domain = [('id', 'in', final_partners)]
        return domain

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

    def send_notification_dash(self):
        # self.retailers = False
        # all_retailers_no_token = self.env['res.users'].sudo().search([('partner_id.is_client', '=', True)])
        # all_retailers = []
        # for ret in all_retailers_no_token:
        #     if ret.user_token:
        #         all_retailers.append(ret)

        # for rec in all_retailers:
        #     self.retailers = [(4, rec.id)]

        # try:
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        # base_url = "https://cms.fayssalbaccar.com"
        all_retailers_no_token = self.env['res.users'].sudo().search([('partner_id.is_client', '=', True)])
        all_retailers = []
        if self.customer_type == '1':
            for ret in all_retailers_no_token:
                if ret.user_token:
                    all_retailers.append(ret)
        elif self.customer_type == '2':
            for ret in self.customers:
                if ret.parent_id:
                    partner_id = ret.parent_id.id
                else:
                    partner_id = ret.id
                retailer = self.env['res.users'].sudo().search([('partner_id', '=', partner_id)])
                if retailer.user_token:
                    all_retailers.append(retailer)

        elif self.customer_type == '3':
            temp_product = []
            for product in self.products:
                temp_product.append(product.id)

            sale_order_lines = self.env['sale.order.line'].sudo().search(
                [('product_id.product_tmpl_id.id', 'in', temp_product)])
            sale_order_ids = sale_order_lines.order_id.ids
            sale_orders = self.env['sale.order'].sudo().search(
                [('id', 'in', sale_order_ids)])

            for sale_order in sale_orders:

                if sale_order.partner_id.is_client:

                    if sale_order.partner_id.parent_id:
                        partner_id = sale_order.partner_id.parent_id.id
                    else:
                        partner_id = sale_order.partner_id.id

                    ret = self.env['res.users'].sudo().search([('partner_id', '=', partner_id)])
                    if ret.user_token:
                        if ret not in all_retailers:
                            all_retailers.append(ret)


        elif self.customer_type == '4':
            partner_list = []
            for zone in self.zones:
                # zone_list.append(zone.id)
                partners = self.env['res.partner'].sudo().search([('zone_id', '=', zone.id)])
                # partners_ids = partners.ids

                for partner in partners:
                    if partner.parent_id:
                        partner_list.append(partner.parent_id.id)

                    partner_list.append(partner.id)

            users = self.env['res.users'].sudo().search([('partner_id', 'in', partner_list)])
            for ret in users:
                if ret.user_token:
                    all_retailers.append(ret)

        notification = Notification
        notif_type = self.notification_type
        notif_type_id = 0

        if self.notification_type == 'promo':
            if self.promotion:
                notif_type_id = self.promotion.id

        elif self.notification_type == 'cat':
            if self.category:
                notif_type_id = self.category.id

        elif self.notification_type == 'plat':
            if self.platdejour:
                notif_type_id = self.platdejour.day_of_week

        if self.image_attachment.id:
            image_full_url = base_url + "/web/content/" + str(self.image_attachment.id)
        else:
            image_full_url = ""
        notifications_saved = self.env['sent.notification'].sudo().create({
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "image_full_url": image_full_url,
            "notif_type": notif_type,
            'notif_type_id': notif_type_id
        })

        for retailer in all_retailers:
            notifications_saved.users = [(4, retailer.id)]
            # notifications_saved = self.env['sent.notification'].sudo().create({
            #     "name": self.name,
            #     "description": self.description,
            #     "users": [(4, retailer.id)] ,
            #     "image": self.image,
            #     "image_full_url":image_full_url,
            #     "notif_type": notif_type,
            #     'notif_type_id':notif_type_id
            #
            # })

            # print('====image_full_url======image_full_url==============',image_full_url)
            notification.send_notification(self.env.user, retailer, self.name, self.description,
                                           notif_type_id, image_full_url, False, notif_type, self.image,
                                           notifications_saved.id)

        self.is_send = True
        self.current_date = datetime.today().date()
        return self.get_message()

    # except:
    #     raise exceptions.UserError("Failed Sending Notification")

    def get_message(self):
        view = self.env.ref('das_sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = "Notification Sent Successfully"
        return {
            'name': 'Success!',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context, }
