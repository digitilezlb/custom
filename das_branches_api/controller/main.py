import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re
from datetime import datetime

from odoo.addons.das_user_notification.controller.main import Notification
import pytz

class BranchesAPI(http.Controller):

    version = ProductInfo.version

    @http.route(version + 'branch/config', type='json', auth='public', methods=['Post','Get'], cors="*")
    def get_config(self, **res):
        detail = ProductInfo()

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
            if company_id:
                restaurant_name = request.env['res.company'].sudo().search([('id', '=', company_id)])
            else:
                restaurant_name = request.env['res.company'].sudo().search([('parent_id', '=', False)], order='id',
                                                                           limit=1)
        except:
            restaurant_name = request.env['res.company'].sudo().search([('parent_id', '=', False)], order='id', limit=1)

        # restaurant_name = request.env['res.company'].sudo().search([('id', '=', request.env.user.company_id.id)])
        if restaurant_name:
            tax = request.env['account.tax'].sudo().search([], limit=1)
            if tax:
                amount_tax = tax.amount
            else:
                amount_tax = 0.0

            calendar = request.env['resource.calendar'].sudo().search(
                [('company_id', '=', restaurant_name.id), ('active', '=', True)])

            restaurant_schedule_time = []
            if calendar:
                calendar_attendance = request.env['resource.calendar.attendance'].sudo().search(
                    [('calendar_id', '=', calendar[0].id)], order='dayofweek ASC,hour_from ASC')

                if calendar_attendance:
                    for att in calendar_attendance:
                        values_att = {
                            "day_name": dict(att._fields['dayofweek'].selection).get(
                                att.dayofweek),
                            "day": int(att.dayofweek) if int(att.dayofweek) <= 6 else 0,
                            "opening_time": detail.format_time_from_float(att.hour_from),
                            "closing_time": detail.format_time_from_float(att.hour_to)
                        }
                        restaurant_schedule_time.append(values_att)
            restaurant_name_arabic = ""
            try:
                if restaurant_name.company_name_ar:
                    restaurant_name_arabic = restaurant_name.company_name_ar
                else:
                    restaurant_name_arabic = ""
            except:
                pass

            restaurant_address_arabic = ''
            try:
                if restaurant_name.street_ar:
                    restaurant_address_arabic = restaurant_name.street_ar
                if restaurant_name.street2_ar:
                    if restaurant_address_arabic != '':
                        restaurant_address_arabic = restaurant_address_arabic + ' ' + restaurant_name.street2_ar
                    else:
                        restaurant_address_arabic = restaurant_name.street2_ar
            except:
                pass

            address = ''

            if restaurant_name.street:
                address = restaurant_name.street
            if restaurant_name.street2:
                if address != '':
                    address = address + ' ' + restaurant_name.street2
                else:
                    address = restaurant_name.street2

            values = {
                "company_id": restaurant_name.id,
                "restaurant_name": restaurant_name.name if restaurant_name.name else "",
                "restaurant_name_arabic": restaurant_name_arabic,
                "restaurant_open_time": "",
                "restaurant_close_time": "",
                "restaurant_address": address,
                "restaurant_name_arabic": restaurant_address_arabic,
                "restaurant_phone": restaurant_name.phone if restaurant_name.phone else "",
                "restaurant_email": restaurant_name.email if restaurant_name.email else "",
                "currency_symbol": restaurant_name.currency_id.name if restaurant_name.currency_id.name else "",
                "currency_symbol_en": restaurant_name.currency_id.name if restaurant_name.currency_id.name else "",
                "currency_id": restaurant_name.currency_id.id,
                "restaurant_logo": "/web/content/" + str(
                    restaurant_name.logo_web_attachment.id) if restaurant_name.logo_web_attachment.id else "",
                "restaurant_logo_dark": "",
                "restaurant_schedule_time": restaurant_schedule_time,
                "restaurant_location_coverage": detail.get_company_zones_witout_id(),
                "minimum_order_value": 1,
                "base_urls": {},
                "tax_percent": amount_tax,
                "delivery_charge": 0,
                "delivery_management": {
                    "status": 1,
                    "min_shipping_charge": 0,
                    "shipping_per_km": 0
                },
                "cash_on_delivery": "true",
                "digital_payment": "true",
                "branches": self.get_branches_information(),
                "terms_and_conditions": restaurant_name.terms_and_conditions if restaurant_name.terms_and_conditions else "",
                "terms_and_conditions_url": restaurant_name.terms_and_conditions_url if restaurant_name.terms_and_conditions_url else "",
                "privacy_policy": restaurant_name.privacy_policy if restaurant_name.privacy_policy else "",
                "privacy_policy_url": restaurant_name.privacy_policy_url if restaurant_name.privacy_policy_url else "",
                "support": restaurant_name.support if restaurant_name.support else "",
                "email_verification": "",
                "phone_verification": "",
                "currency_symbol_position": "left" if restaurant_name.currency_id.position == "before" else "right",
                "maintenance_mode": False,
                "country": "",
                "self_pickup": "true",
                "delivery": "true",
                "social_media_link": [
                    {
                        "id": 1,
                        "name": "twitter",
                        "link": restaurant_name.social_twitter if restaurant_name.social_twitter else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 2,
                        "name": "facebook",
                        "link": restaurant_name.social_facebook if restaurant_name.social_facebook else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 3,
                        "name": "gitHub",
                        "link": restaurant_name.social_github if restaurant_name.social_github else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 4,
                        "name": "linkedIn",
                        "link": restaurant_name.social_linkedin if restaurant_name.social_linkedin else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 5,
                        "name": "youtube",
                        "link": restaurant_name.social_youtube if restaurant_name.social_youtube else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 6,
                        "name": "instagram",
                        "link": restaurant_name.social_instagram if restaurant_name.social_instagram else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    },
                    {
                        "id": 7,
                        "name": "whatsapp",
                        "link": restaurant_name.whatsapp if restaurant_name.whatsapp else "",
                        "status": 1,
                        "created_at": "",
                        "updated_at": ""
                    }
                ],

                "play_store_config": {
                    "status": "false",
                    "link": "",
                    "min_version": "1"
                },
                "app_store_config": {
                    "status": "false",
                    "link": "",
                    "min_version": "1"
                },
                "software_version": "1.0",
                "footer_text": "copyright © Digitile",
                "decimal_point_settings": 2,
                "schedule_order_slot_duration": 0,
                "time_format": "12",
                "promotion_campaign": [],
                "social_login": {
                    "google": 0,
                    "facebook": 0
                },
                "wallet_status": 0,
                "loyalty_point_status": 0,
                "ref_earning_status": 0,
                "loyalty_point_item_purchase_point": 0,
                "loyalty_point_exchange_rate": 0,
                "loyalty_point_minimum_point": 0,
                "digital_payment_status": 1,
                "active_payment_method_list": [],
                "whatsapp": {
                    "status": 1,
                    "number": ""
                },
                "cookies_management": {
                    "status": 0,
                    "text": "Allow Cookies for this site"
                },
                "toggle_dm_registration": 0,
                "is_veg_non_veg_active": 0,
                "otp_resend_time": 60,
                "theme": {
                    "colors": {
                        "main_color": "#E97424",
                        "main_dark_color": "#E97424",
                        "secondary_color": "#E97424",
                        "secondary_dark_color": "#E97424"
                    }
                },
                "categories_per_slide": 7,
                "default_language": "en",
                "business_type": 1,
                "tax_enabled": 1

            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Config Found'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}

        return response

    def get_branches_information(self):
        detail = ProductInfo()
        branches = request.env['res.company'].sudo().search([])
        branch_list = []
        if branches:
            for branch in branches:
                address = ""
                if branch.city:
                    address = branch.city
                if branch.street:
                    if address != "":
                        address = address + ' , ' + branch.street
                    else:
                        address = branch.street
                if branch.street2:
                    if address != "":
                        address = address + ' , ' + branch.street2
                    else:
                        address = branch.street2

                values = {
                    "id": branch.id,
                    "name": branch.name,
                    "email": branch.email,
                    "longitude": branch.partner_id.partner_longitude,
                    "latitude": branch.partner_id.partner_latitude,
                    "address": address,
                    "coverage": 0,
                    "zones": detail.get_company_zones_witout_id(branch.id),
                }
                branch_list.append(values)

        return branch_list

    @http.route(version + 'branch/current-orders', type='json', auth='user', methods=['Post','Get'], cors="*")
    def get_current_orders(self):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])


        order_list = self.get_orders(user.company_id,"Delivered",False)
        if user:
            if len(order_list):
                Response.status = '200'
                response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
            else:
                Response.status = '200'
                response = {'status': 200,'response': order_list, 'message': 'No Order Found!'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': order_list, 'message': 'User Not Found!'}
        return response


    def get_orders(self, company_id, order_status=None,order_status_Is_or_not =None):

        order_list = []

        if order_status == "Draft":
            order_status_id = "2"
        elif order_status == "Confirmed":
            order_status_id = "3"
        elif order_status == "In Progress":
            order_status_id = "4"
        elif order_status == "Ready":
            order_status_id = "5"
        elif order_status == "Out For Delivery":
            order_status_id = "6"
        elif order_status == "Delivered":
            order_status_id = "7"

        detail = ProductInfo()
        if company_id:

            if order_status:
                if order_status_Is_or_not:
                    sale_orders = request.env['sale.order'].sudo().search(
                            [('company_id', '=', company_id.id), ('sale_order_type', '!=', "3"),('state', '!=', 'cancel'),
                            ('order_status', '=', order_status_id)],order='create_date Desc')
                else:
                   sale_orders = request.env['sale.order'].sudo().search(
                            [('company_id', '=', company_id.id), ('sale_order_type', '!=', "3"),('state', '!=', 'cancel'),
                             ('order_status', '!=', order_status_id)],order='create_date Desc')


            else:
                sale_orders = request.env['sale.order'].sudo().search([('company_id', '=', company_id.id),('sale_order_type', '!=', "3"),('state', '!=', 'cancel')])

            delivery_product = request.env['product.product'].sudo().search(
                                [('is_delivery', '=', True)], limit=1)
            
            
             
            if sale_orders:
                for sale_order in sale_orders:
                    delivery_charge = 0
                    if sale_order.sale_order_type == "1":

                        for line in sale_order.order_line:

                            if delivery_product.id == line.product_id.id:
                                delivery_charge = line.price_total
                    else:
                        delivery_charge = 0

                    address = ""
                    if sale_order.partner_shipping_id.city:
                        address = sale_order.partner_shipping_id.city
                    if sale_order.partner_shipping_id.street:
                        if address != "":
                            address = address + ' , ' + sale_order.partner_shipping_id.street
                        else:
                            address = sale_order.partner_shipping_id.street
                    if sale_order.partner_shipping_id.street2:
                        if address != "":
                            address = address + ' , ' + sale_order.partner_shipping_id.street2
                        else:
                            address = sale_order.partner_shipping_id.street2

                    orders = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', sale_order.partner_id.id),('company_id', '=', company_id.id), ('sale_order_type', '!=', "3")])
                    if orders:
                        orders_count = len(orders)
                    else:
                        orders_count = 0

                    if sale_order.order_status == "2":
                        theorder_status_id = "Draft"
                    elif sale_order.order_status == "3":
                        theorder_status_id = "Confirmed"
                    elif sale_order.order_status == "4":
                        theorder_status_id = "In Progress"
                    elif sale_order.order_status == "5":
                        theorder_status_id = "Ready"
                    elif sale_order.order_status == "6":
                        theorder_status_id = "Out For Delivery"
                    elif sale_order.order_status == "7":
                        theorder_status_id = "Delivered"

                    preparation_time = detail.get_preparation_time(sale_order)
                    if preparation_time==0:
                        preparation_time_str="0"
                    else:
                        preparation_time_str = str(preparation_time)
                    
                    if sale_order.assign_time_time:
                        current_time = sale_order.assign_time_time.astimezone(ProductInfo.beirut_timezone)
                    else:
                        current_time = None
                        
                    values = {
                        "id": sale_order.id,
                        "name": sale_order.name,
                        "user_id": sale_order.user_id.id if sale_order.user_id else 0,
                        "order_amount": sale_order.amount_total,
                        "coupon_discount_amount": 0,
                        "coupon_discount_title": "",
                        "payment_status": "unpaid",
                        "order_status": theorder_status_id,
                        "order_time_to_be_ready": sale_order.order_time_to_be_ready if sale_order.order_time_to_be_ready else None,
                        "assign_time_time": current_time , # sale_order.assign_time_time if sale_order.assign_time_time else None,
                        "total_tax_amount": sale_order.amount_tax,
                        "payment_method": "cash_on_delivery",
                        "transaction_reference": "",
                        "delivery_address_id": sale_order.partner_shipping_id.id,
                        "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                        "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                        "checked": 1,
                        "delivery_man_id": sale_order.driver_id.id if sale_order.driver_id else None,
                        "delivery_charge": delivery_charge,
                        "order_note": "",
                        "coupon_code": "",
                        "order_type": "delivery" if sale_order.sale_order_type == "1" else "Pick Up",
                        "branch_id": 1,
                        "callback": "",
                        "delivery_date": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).date() if sale_order.delivery_date else None,
                        "delivery_time": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).time() if sale_order.delivery_date else None,
                        "extra_discount": "0.00",
                        "delivery_address": {
                            "id": sale_order.partner_shipping_id.id,
                            "address_type": sale_order.partner_shipping_id.type,
                            "contact_person_number": sale_order.partner_shipping_id.mobile if sale_order.partner_shipping_id.mobile else sale_order.partner_shipping_id.phone if sale_order.partner_shipping_id.phone else "",
                            "floor": "",
                            "house": "",
                            "road": sale_order.partner_shipping_id.street if sale_order.partner_shipping_id.street else "",
                            "address": address,
                            "latitude": sale_order.partner_shipping_id.partner_latitude,
                            "longitude": sale_order.partner_shipping_id.partner_longitude,
                            "created_at": sale_order.partner_shipping_id.create_date,
                            "updated_at": sale_order.partner_shipping_id.write_date,
                            "user_id": sale_order.partner_shipping_id.user_id.id if sale_order.partner_shipping_id.user_id else 0,
                            "contact_person_name": sale_order.partner_shipping_id.name  if sale_order.partner_shipping_id.name else "",
                        },
                        "preparation_time": preparation_time_str,
                        "table_id": "",
                        "number_of_people": "",
                        "table_order_id": "",

                        "customer": {
                            "id": sale_order.partner_id.id,
                            "f_name": sale_order.partner_id.name,
                            "l_name": "",
                            "email": sale_order.partner_id.email if sale_order.partner_id.email else "",
                            "user_type": "",
                            "is_active": 1,
                            "image": "/web/content/" + str(sale_order.partner_id.team_member_image_attachment.id) if sale_order.partner_id.team_member_image_attachment.id else "",
                            "is_phone_verified": 0,
                            "email_verified_at": "",
                            "created_at": sale_order.partner_id.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.partner_id.write_date.astimezone(ProductInfo.beirut_timezone),
                            "email_verification_token": "",
                            "phone": sale_order.partner_id.mobile if sale_order.partner_id.mobile else sale_order.partner_id.phone if sale_order.partner_id.phone else "",
                            "cm_firebase_token": "",
                            "point": 0,
                            "temporary_token": "",
                            "login_medium": "",
                            "wallet_balance": "0.000",
                            "refer_code": "null",
                            "refer_by": "null",
                            "login_hit_count": 0,
                            "is_temp_blocked": 0,
                            "temp_block_time": "null",
                            "orders_count": orders_count

                        }
                    }
                    order_list.append(values)
        # returnvalues={
        #     "list":order_list,
        #     "total_size":len(sale_orders) if sale_orders else 0
        # }
        return order_list



    @http.route(version + 'branch/all-orders', type='json', auth='user', methods=['Post','Get'], cors="*")
    def get_all_orders(self):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        order_list = []

        order_list = self.get_orders(user.company_id)


        if user:
            if len(order_list):
                Response.status = '200'
                response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
            else:
                Response.status = '200'
                response = {'status': 200,'response': order_list, 'message': 'No Order Found!'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': order_list, 'message': 'User Not Found!'}
        return response

    def get_completed_orders_list(self, company_id,limit,offset):

        order_list = []


        order_status_id = "7"

        detail = ProductInfo()
        if company_id:
            #'|', '&', '&', ('field_A', '=', True), ('field_B', '=', True), ('field_C', '=', True), '&', ('field_A', '=', True), ('field_B', '=', True), ('field_D', '=', True)

            sale_orders_delivered = request.env['sale.order'].sudo().search([('company_id', '=', company_id.id), ('sale_order_type', '!=', "3"),('order_status', '=', order_status_id)])
            sale_orders_canccel = request.env['sale.order'].sudo().search([('company_id', '=', company_id.id), ('sale_order_type', '!=', "3"),('state', '=', 'cancel')])

            sale_orders = request.env['sale.order'].sudo().search(
                            ['|',  ('id', 'in', sale_orders_delivered.ids), ('id', 'in', sale_orders_canccel.ids)],order='create_date Desc',limit=limit,offset=limit*offset)



            if sale_orders:
                delivery_product = request.env['product.product'].sudo().search(
                                [('is_delivery', '=', True)], limit=1)
                for sale_order in sale_orders:

                    if sale_order.sale_order_type == "1":

                        
                        # lines = request.env['sale.order.line'].sudo().search([('order_id','=',sale_order.id)])
                        delivery_charge = 0
                        for line in sale_order.order_line:

                            if delivery_product.id == line.product_id.id:
                                delivery_charge = line.price_total
                    else:
                        delivery_charge = 0

                    address = ""
                    if sale_order.partner_shipping_id.city:
                        address = sale_order.partner_shipping_id.city
                    if sale_order.partner_shipping_id.street:
                        if address != "":
                            address = address + ' , ' + sale_order.partner_shipping_id.street
                        else:
                            address = sale_order.partner_shipping_id.street
                    if sale_order.partner_shipping_id.street2:
                        if address != "":
                            address = address + ' , ' + sale_order.partner_shipping_id.street2
                        else:
                            address = sale_order.partner_shipping_id.street2

                    orders = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', sale_order.partner_id.id),('company_id', '=', company_id.id), ('sale_order_type', '!=', "3")])
                    if orders:
                        orders_count = len(orders)
                    else:
                        orders_count = 0

                    if sale_order.order_status == "2":
                        theorder_status_id = "Draft"
                    elif sale_order.order_status == "3":
                        theorder_status_id = "Confirmed"
                    elif sale_order.order_status == "4":
                        theorder_status_id = "In Progress"
                    elif sale_order.order_status == "5":
                        theorder_status_id = "Ready"
                    elif sale_order.order_status == "6":
                        theorder_status_id = "Out For Delivery"
                    elif sale_order.order_status == "7":
                        theorder_status_id = "Delivered"

                    if sale_order.state == "cancel":
                        theorder_status_id = "Canceled"

                    preparation_time = detail.get_preparation_time(sale_order)
                    if preparation_time==0:
                        preparation_time_str="0"
                    else:
                        preparation_time_str = str(preparation_time)
                    
                    if sale_order.assign_time_time:
                        current_time = sale_order.assign_time_time.astimezone(ProductInfo.beirut_timezone)
                    else:
                        current_time = None
                        
                    values = {
                        "id": sale_order.id,
                        "name": sale_order.name,
                        "user_id": sale_order.user_id.id if sale_order.user_id else 0,
                        "order_amount": sale_order.amount_total,
                        "coupon_discount_amount": 0,
                        "coupon_discount_title": "",
                        "payment_status": "unpaid",
                        "order_status": theorder_status_id,
                        "order_time_to_be_ready": sale_order.order_time_to_be_ready if sale_order.order_time_to_be_ready else None,
                        "assign_time_time": current_time, # sale_order.assign_time_time if sale_order.assign_time_time else None,
                        "total_tax_amount": sale_order.amount_tax,
                        "payment_method": "cash_on_delivery",
                        "transaction_reference": "",
                        "delivery_address_id": sale_order.partner_shipping_id.id,
                        "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                        "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                        "checked": 1,
                        "delivery_man_id": sale_order.driver_id.id if sale_order.driver_id else None,
                        "delivery_charge": delivery_charge,
                        "order_note": "",
                        "coupon_code": "",
                        "order_type": "delivery" if sale_order.sale_order_type == "1" else "Pick Up",
                        "branch_id": 1,
                        "callback": "",
                        "delivery_date": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).date() if sale_order.delivery_date else None,
                        "delivery_time": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).time() if sale_order.delivery_date else None,
                        "extra_discount": "0.00",
                        "delivery_address": {
                            "id": sale_order.partner_shipping_id.id,
                            "address_type": sale_order.partner_shipping_id.type,
                            "contact_person_number": sale_order.partner_shipping_id.mobile if sale_order.partner_shipping_id.mobile else sale_order.partner_shipping_id.phone if sale_order.partner_shipping_id.phone else "",
                            "floor": "",
                            "house": "",
                            "road": sale_order.partner_shipping_id.street,
                            "address": address,
                            "latitude": sale_order.partner_shipping_id.partner_latitude,
                            "longitude": sale_order.partner_shipping_id.partner_longitude,
                            "created_at": sale_order.partner_shipping_id.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.partner_shipping_id.write_date.astimezone(ProductInfo.beirut_timezone),
                            "user_id": sale_order.partner_shipping_id.user_id.id if sale_order.partner_shipping_id.user_id else 0,
                            "contact_person_name": sale_order.partner_shipping_id.name if sale_order.partner_shipping_id.name else ""
                        },
                        "preparation_time": preparation_time_str,
                        "table_id": "",
                        "number_of_people": "",
                        "table_order_id": "",

                        "customer": {
                            "id": sale_order.partner_id.id,
                            "f_name": sale_order.partner_id.name,
                            "l_name": "",
                            "email": sale_order.partner_id.email if sale_order.partner_id.email else "",
                            "user_type": "",
                            "is_active": 1,
                            "image": "/web/content/" + str(sale_order.partner_id.team_member_image_attachment.id) if sale_order.partner_id.team_member_image_attachment.id else "",
                            "is_phone_verified": 0,
                            "email_verified_at": "",
                            "created_at": sale_order.partner_id.create_date,
                            "updated_at": sale_order.partner_id.write_date,
                            "email_verification_token": "",
                            "phone": sale_order.partner_id.mobile if sale_order.partner_id.mobile else sale_order.partner_id.phone if sale_order.partner_id.phone else "",
                            "cm_firebase_token": "",
                            "point": 0,
                            "temporary_token": "",
                            "login_medium": "",
                            "wallet_balance": "0.000",
                            "refer_code": "null",
                            "refer_by": "null",
                            "login_hit_count": 0,
                            "is_temp_blocked": 0,
                            "temp_block_time": "null",
                            "orders_count": orders_count

                        }
                    }
                    order_list.append(values)
        returnvalues={
            "list":order_list,
            "total_size":len(sale_orders) if sale_orders else 0,
            "limit":limit,
            "offset":offset
        }
        return returnvalues


    @http.route(version + 'branch/completed-orders', type='json', auth='user', methods=['Post','Get'], cors="*")
    def get_completed_orders(self):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        req = json.loads(request.httprequest.data)

        limit = req.get('limit')
        offset = req.get('offset')



        order_list = self.get_completed_orders_list(user.company_id,  limit,offset)
        if user:
            if len(order_list['list']):
                Response.status = '200'
                response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
            else:
                Response.status = '200'
                response = {'status': 200,'response': order_list, 'message': 'No Order Found!'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': order_list, 'message': 'User Not Found!'}
        return response


    @http.route(version + 'branch/order-details', type='json',   auth='user', methods=['Post','Get'],
                cors="*")
    def get_order_details(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        order_id = req.get('order_id')

        Product_Info = ProductInfo()
        order_list = []
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        if user:
            if sale_order:
                delivery_product = request.env['product.product'].sudo().search(
                    [('is_delivery', '=', True)], limit=1)
                for line in sale_order.order_line:
                    # product = request.env['product.product'].sudo().search([('id','=',)])
                    if delivery_product.id != line.product_id.id:
                        if line.product_id.description:
                            desc = re.sub(r'<.*?>', ' ', line.product_id.description)
                        else:
                            desc = ''
                        desc = desc.strip()
    
                        taxes = line.product_id.taxes_id
                        amount = 0.0
                        for tax in taxes:
                            amount = tax.amount
    
                        values = {
    
                            "id": line.id,
                            "product_id": line.product_id.id,
                            "order_id": order_id,
                            "price": line.price_total,
                            "price_list": Product_Info.get_prices_for_currency_list(line.price_total,sale_order.company_id.id),
                            "product_details": {
                                "id": line.product_id.id,
                                "name": line.product_id.name,
                                "description": desc,
                                "kitchen_note": line.kitchen_notes if line.kitchen_notes else "",
                                "image": "/web/content/" + str(
                                    line.product_id.image_attachment.id) if line.product_id.image_attachment.id else "",
                                # "price": Product_Info.get_product_product_price(line.product_id),
                                "price": round(line.price_total/line.product_uom_qty,2),
                                "price_list": Product_Info.get_prices_for_currency_list(line.price_total/line.product_uom_qty,sale_order.company_id.id),
                                "file_en": None,
                                "file_ar": None,
                                "variations": [],
                                "add_ons": [],
                                "extra_products": "[]",
                                "required_ingredients": [],
                                "removable_ingredients": [],
                                "tax": amount,
                                "available_time_starts": "",
                                "available_time_ends": "",
                                "status": 1,
                                "created_at": line.product_id.create_date.astimezone(ProductInfo.beirut_timezone),
                                "updated_at": line.product_id.write_date.astimezone(ProductInfo.beirut_timezone),
                                "attributes": [],
                                "category_ids": [],
                                "choice_options": [],
                                "discount": 0,
                                "discount_type": "percent",
                                "tax_type": "percent",
                                "set_menu": 0,
                                "popularity_count": 1,
                                "product_type": "",
                                "slug": "",
                                "stock": 0,
                                "unit": None,
                                "addon_details": [],
                                "removableIngredient_details": [],
                                "translations": []
                            },
                            "variation": Product_Info.get_attribute_product_product_as_mannasat(line.product_id, 'en'),
                            "discount_on_product": 0,
                            "discount_type": "discount_on_product",
                            "quantity": line.product_uom_qty,
                            "tax_amount": line.price_tax,
                            "created_at": line.create_date,
                            "updated_at": line.write_date,
                            "add_on_ids": [],
                            "variant": [],
                            "add_on_qtys": [],
                            "removable_ingredient_ids": [],
                            "extra_products_details": "[]",
                            "add_on_taxes": [],
                            "add_on_prices": [],
                            "add_on_tax_amount": 0,
                            "review_count": 0,
                            "is_product_available": 1,
                            "delivery_time": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).time() if sale_order.delivery_date else None,
                            "delivery_date": sale_order.delivery_date.astimezone(ProductInfo.beirut_timezone).date() if sale_order.delivery_date else None,
                            "preparation_time": line.product_id.preparing_time,
                            "add_ons": None,
                            "item_details": None
                        }
                        order_list.append(values)
                        
                deliveryman={}
                if sale_order.driver_id:
                    deliveryman={
                        'id':sale_order.driver_id.id,
                        'name':sale_order.driver_id.name,
                        'phone':sale_order.driver_id.mobile if sale_order.driver_id.mobile else "",
                        'email':sale_order.driver_id.email if sale_order.driver_id.email else "",
                        'image':"/web/content/" + str(sale_order.driver_id.team_member_image_attachment.id) if sale_order.driver_id.team_member_image_attachment.id else ""
                    }
                Response.status = '200'
                response = {'status': 200, 'details': order_list,'deliveryman':deliveryman, 'message': 'Sale Order Details Found'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'No data Found!'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}

        return response

    @http.route(version + 'branch/delivery-men', type='json', auth='user', methods=['Post','Get'],
                cors="*")
    def get_delivery_men(self):

        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])


        Product_Info = ProductInfo()
        driver_list = []

        if user:
            drivers = request.env['res.partner'].sudo().search([('is_driver','=',True),('company_id','=',user.company_id.id)])
            # drivers = request.env['res.partner'].sudo().search([('is_driver','=',True),('company_id','in',[user.company_id.id, None])])
            if drivers:
                for driver in drivers:
                    # _sql = "select sale_order.order_status ,count(sale_order.id) as count_of_order "
                    # _sql += " from sale_order"
                    # _sql += " where sale_order.driver_id=" + str(driver.id)
                    # _sql += "  group by sale_order.order_status order by count_of_order Desc"
                    # request.cr.execute(_sql)
                    # order_statuses = request.cr.fetchall()
                    # print('====order_statuses=========order_statuses=====', order_statuses)
                    order_status_list=[]
                    for i in range(2,7):
                        order_status = str(i)
                        
                        orders = request.env['sale.order'].sudo().read_group(
                            [('driver_id', '=', driver.id),('order_status','=',order_status)],
                            ['order_status', 'count_of_order:count(id)'],
                            ['order_status']
                        )
                        if order_status == '2':
                            order_status_name = 'Draft'
                        elif order_status == '3':
                            order_status_name = 'Confirmed'
                        elif order_status == '4':
                            order_status_name = 'In Progress'
                        elif order_status == '5':
                            order_status_name = 'Ready'
                        elif order_status == '6':
                            order_status_name = 'Out For Delivery'
                        if len(orders) > 0:

                            value = {
                                "order_status": order_status,
                                "order_status_name": order_status_name,
                                "count_of_order": orders[0]['count_of_order']
                            }
                        else:
                            value={
                                "order_status": order_status,
                                "order_status_name": order_status_name,
                                "count_of_order": 0
                            }
                        order_status_list.append(value)


                    driver_name = driver.name
                    
                    values={
                        "id": driver.id,
                        "first_name": driver_name ,
                        "last_name": "",
                        "order_status_list": order_status_list
                    }
                    driver_list.append(values)
                Response.status = '200'
                response = {'status': 200, 'response': driver_list, 'message': 'Drivers Found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'No driver Found!'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}

        return response

    @http.route(version + 'branch/delivery-men-out-for-delivery', type='json', auth='user', methods=['Post', 'Get'],
                cors="*")
    def get_delivery_men_out_for_delivery(self):

        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        Product_Info = ProductInfo()
        driver_list = []

        if user:
            drivers = request.env['res.partner'].sudo().search(
                [('is_driver', '=', True), ('company_id', '=', user.company_id.id)])

            if len(drivers)>0:
                for driver in drivers:
                    sales = request.env['sale.order'].sudo().search([('driver_id', '=',driver.id),('order_status', '=','6')])
                    if len(sales) > 0:
                        sale_list=[]
                        for sale in sales:
                            sale_value={
                                'sale_name':sale.name,
                                'client_id':sale.partner_id.id,
                                'client_name':sale.partner_id.name,
                                'client_latitude': sale.partner_shipping_id.partner_latitude,
                                'client_longitude': sale.partner_shipping_id.partner_longitude,
                            }
                            sale_list.append(sale_value)
                        values = {
                            "id": driver.id,
                            "first_name": driver.name,
                            "last_name": "",
                            "sale_list":sale_list
                        }
                        driver_list.append(values)
                Response.status = '200'
                response = {'status': 200, 'response': driver_list, 'message': 'Drivers Found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'No driver Found!'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}

        return response

    @http.route(version + 'branch/delivery-man-tracking', type='json', auth='user', methods=['Post', 'Get'],
                cors="*")
    def get_delivery_man_tracking(self):

        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        driver_id = req.get('driver_id')

        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        Product_Info = ProductInfo()
        location_list = []

        if user:

            sales = request.env['sale.order'].sudo().search(
                [('driver_id', '=', driver_id), ('order_status', '=', '6')])

            if len(sales)>0:
                order_locations = request.env['driver.order.location.data'].sudo().search([('order_id', 'in', sales.ids)],
                                                                                           order='create_date desc')

                order_location_list = []
                if order_locations:

                    for order_location in order_locations:
                        values = {
                            'latitude': order_location.latitude,
                            'longitude': order_location.longitude,
                            'location': order_location.location,
                            'date': order_location.create_date,
                            'order_name':order_location.order_id.name

                        }
                        order_location_list.append(values)
                Response.status = '200'
                response = {'status': 200, 'response': order_location_list, 'message': 'Locations List Found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'No Order Found!'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}

        return response
    @http.route(version + 'branch/orders/assign-delivery-man', type='json', auth='user', methods=['Post','PUT'],
                cors="*")
    def get_assign_delivery_man(self):


        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        driver_id = req.get('driver_id')
        order_time_to_be_ready = req.get('order_time_to_be_ready')
        order_id = req.get('order_id')
        old_driver_id = req.get('old_driver_id')
        if user:
            now_utc = datetime.now(pytz.UTC)
            current_time = now_utc.astimezone(ProductInfo.beirut_timezone)
            vals={
                "driver_id":driver_id,
                "order_time_to_be_ready":str(order_time_to_be_ready),
                # "assign_time_time":current_time

            }
            
            sale_order = request.env['sale.order'].sudo().search([('id','=',order_id)])
            if sale_order:
                sale_order.write(vals)
                Response.status = '200'
                response = {'status': 200, 'message': 'Sale Order Updated'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        
        # try:
        if old_driver_id:
            if driver_id:
                if old_driver_id!=driver_id:
                    driver = request.env['res.partner'].sudo().search([('id', '=', old_driver_id)], limit=1)

                    driver_user = request.env['res.users'].sudo().search([('partner_id', '=', driver.id)], limit=1)
                    notification = Notification
                    message_name = "حذف طلبية"

                    message_description = "لقد تم حذف الطلبية رقم " + sale_order.name
                    Response.status = '200'
                    response = {'status': 200, 'old_driver_id': old_driver_id,'driver_id': driver_id,'message': 'Sale Order Updated'}

                    notification.send_notification(request.env.user, driver_user, message_name, message_description,
                                                       sale_order.id)

        # except:
        #     pass

        return response


    @http.route(version + 'branch/update-order-status', type='json', auth='user', methods=['Post'],
                cors="*")
    def update_order_status(self):

        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('order_id')
        order_status = req.get('status')

        # if order_status:
        #     Response.status = '404'
        #     response = {'status': 404, 'message': 'Status Not Found!'}
        #
        #     return response

        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            if sale_order:
                if order_status == 'delivered':
                    order_status_id = '7'
                elif order_status == 'out_for_delivery':
                    order_status_id = '6'
                elif order_status == 'ready':
                    order_status_id = '5'
                elif order_status == 'in_progress':
                    order_status_id = '4'
                elif order_status == 'confirmed':
                    order_status_id = '3'

                sale_order.write(
                    {'order_status': order_status_id}
                )

                delivery_product = request.env['product.product'].sudo().search(
                    [('is_delivery', '=', True)], limit=1)

                # try:

                if order_status_id == '3':

                    notification = Notification
                    message_name = "تأكيد طلبية"

                    message_description = "لقد تم تأكيد الطلبية رقم " + sale_order.name


                    # client_user = request.env['res.users'].sudo().search([('partner_id','=',sale_order.partner_id.id)])

                    if sale_order.partner_id.parent_id:
                        partner_id = sale_order.partner_id.parent_id.id
                    else:
                        partner_id = sale_order.partner_id.id
                    client_user = request.env['res.users'].sudo().search(
                        [('partner_id', '=', partner_id)])


                    if client_user:
                        notif = notification.send_notification(request.env.user, client_user, message_name,
                                                   message_description,
                                                   sale_order.id)
                        # Response.status = '200'
                        # response = {'status': 200,'notif':notif,'order_status_id':order_status_id,'client_user':message_description, 'message': 'Sale Order Status Changed!'}
                        # return response
                    # try:
                    nb_orderline = len(sale_order.order_line)

                    nb_product_delivery = 0
                    nb_product_ready = 0

                    for line in sale_order.order_line:

                        product = line.product_id
                        if product != delivery_product:
                            if product.kitchen_id:
                                kitchen_id = product.kitchen_id.id
                            else:
                                kitchen_id = self.get_default_kitchen(sale_order.company_id)

                            if kitchen_id != -1:
                                kitchen_ready_id = self.get_ready_kitchen(sale_order.company_id)
                                if kitchen_ready_id !=-1:
                                    if kitchen_ready_id == kitchen_id:
                                        nb_product_ready = nb_product_ready + 1
                                        line.write({
                                            'order_status':'5'
                                        })
                        else:
                            nb_product_delivery = 1
                    if nb_orderline == (nb_product_delivery +  nb_product_ready):
                        sale_order.action_confirm()
                        sale_order.write({
                            'order_status': '5'
                        })

                    # except:
                    #     pass
                # except:
                #     pass
                
                # try:
                if order_status_id == '4':
                    notification = Notification
                    message_name = "طلبية الى المطبخ"
                    message_description = "لقد تم تحويل الطلبية رقم " + sale_order.name + " الى المطبخ"



                    order_lines = request.env['digitile.order.kitchen.line'].sudo().search(
                        [('order_kitchen_id', '=', sale_order.id)])
                    add_product = False
                    for line in sale_order.order_line:
                        product = line.product_id
                        if product != delivery_product:
                            if product.kitchen_id:
                                kitchen_id = product.kitchen_id.id
                            else:
                                kitchen_id = self.get_default_kitchen(sale_order.company_id)

                            if kitchen_id!=-1:
                                partner_ids = request.env['res.partner'].sudo().search([('kitchen_id','=',kitchen_id)])
                                if partner_ids:
                                    for partner_id in partner_ids:
                                        chef_users = request.env['res.users'].sudo().search([('partner_id','=',partner_id.id)])
                                        if chef_users:
                                            for chef_user in chef_users:
                                                notification.send_notification(request.env.user, chef_user, message_name,
                                                                       message_description,
                                                                       sale_order.id)
                # except:
                #     pass

                # if order_status_id == '7':
                #     order_trip = request.env['orders.trip'].sudo().search([('order_ids', 'in', sale_order.id)])
                #     if order_trip:
                #         is_delivered = True
                #         for inv in order_trip.order_ids:
                #             if inv.order_status != '7':
                #                 is_delivered = False
                #         if is_delivered:
                #             order_trip.write(
                #                 {'state': 'arrived'}
                #             )
                Response.status = '200'
                response = {'status': 200,  'message': 'Sale Order Status Changed!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}

        return response
        
    def get_default_kitchen(self,company_id):
        if company_id:
            kitchen_id = request.env['digitile.kitchen'].sudo().search([('company_id','=',company_id.id),('default_kitchen','=',True)])
            if kitchen_id:
                return kitchen_id.id
            else:
                return -1
        else:
            return -1

    def get_ready_kitchen(self,company_id):
        if company_id:
            kitchen_id = request.env['digitile.kitchen'].sudo().search([('company_id','=',company_id.id),('ready_kitchen','=',True)])
            if kitchen_id:
                return kitchen_id.id
            else:
                return -1
        else:
            return -1
    @http.route(version + 'branch/cancel-order', type='json', auth='user', methods=['Post'],cors="*")
    def cancel_order(self):
        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('order_id')

        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            if sale_order:
                sale_order.write(
                    {
                        'state':'cancel'
                    }
                )

                Response.status = '200'
                response = {'status': 200, 'message': 'Sale Order Canceled!'}
                
                # try:
                notification = Notification
                message_name = "إلغاء طلبية"

                message_description = "لقد تم إلغاء الطلبية رقم " + sale_order.name


                client_user = request.env['res.users'].sudo().search([('partner_id','=',sale_order.partner_id.id)])
                # prin('------------------------------------',client_user)
                if client_user:
                    notification.send_notification(request.env.user, client_user, message_name,
                                               message_description,
                                               sale_order.id)
                # except:
                #     pass
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}

        return response
