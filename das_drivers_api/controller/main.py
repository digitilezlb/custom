import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re
from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification
import pytz

class DriversAPI(http.Controller):
    version = "/api/"

    # @http.route(version + 'delivery-man/record-location-data', type='json', auth='public', methods=['Post'], cors="*")
    @http.route(version + 'delivery-man/record-location-data', type='json', auth='user', methods=['Post'], cors="*")
    def record_location_data(self, **res):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if user.partner_id:
            req = json.loads(request.httprequest.data)
            order_id = req.get('order_id')
            driver_id = user.partner_id
            latitude = req.get('latitude')
            longitude = req.get('longitude')
            location = req.get('location')
            
            order_locations = request.env['driver.order.location.data'].sudo().search([('order_id', '=', order_id)])

            if order_locations:
                is_tracked = True
            else:
                is_tracked = False


            order_location = request.env['driver.order.location.data'].sudo().create({
                "driver_id": driver_id.id,
                "order_id": order_id,
                "latitude": latitude,
                "longitude": longitude,
                "location": location,

            })
            # sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            #
            # if sale_order.order_status=='6':
            #     if is_tracked==True:
            #         Response.status = '200'
            #         response = {'status': 200,'orders':order_locations, 'message': 'Location tracked Received'}
            #         return response
            #     else:
            #
            #         if sale_order.partner_id.parent_id:
            #             partner_id = sale_order.partner_id.parent_id.id
            #         else:
            #             partner_id = sale_order.partner_id.id
            #         client_user = request.env['res.users'].sudo().search(
            #             [('partner_id', '=', partner_id)])
            #
            #         if client_user:
            #
            #             notification = Notification
            #             message_name = "قيد الوصول123"
            #
            #             message_description = "الطلبية رقم " + sale_order.name + " أصبحت قيد الوصول"
            #
            #             chat_id = '1'
            #
            #             notification.send_notification(request.env.user, client_user, message_name,
            #                                                message_description,
            #                                            sale_order.id)
            #             Response.status = '200'
            #             response = {'status': 200, 'message': 'Location First Received'}
            #             return response

                # else:
                #     print('==========================no notify========')
            
            Response.status = '200'
            response = {'status': 200,   'message': 'Location Received'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Location Found!'}
        return response
    
    @http.route(version + 'delivery-man/is-tracked-order', type='json', auth='public', methods=['Post'], cors="*")
    def is_tracked_order(self, **res):
        req = json.loads(request.httprequest.data)
        order_id = req.get('order_id')
        order_locations = request.env['driver.order.location.data'].sudo().search([('order_id', '=', order_id)])
        if order_locations:
            is_tracked = True
        else:
            is_tracked = False


        ##############################################################
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        if sale_order.order_status == '6':
            if is_tracked == True:

                if sale_order.partner_id.parent_id:
                    partner_id = sale_order.partner_id.parent_id.id
                else:
                    partner_id = sale_order.partner_id.id
                client_user = request.env['res.users'].sudo().search(
                    [('partner_id', '=', partner_id)])

                order_locations = request.env['driver.order.location.data'].sudo().search([('order_id', '=', order_id)])

                if client_user and len(order_locations)==1:
                    notification = Notification
                    message_name = "قيد الوصول"

                    message_description = "الطلبية رقم " + sale_order.name + " أصبحت قيد الوصول"

                    chat_id = '1'

                    notification.send_notification(request.env.user, client_user, message_name,
                                                   message_description,
                                                   sale_order.id)
                    # Response.status = '200'
                    # response = {'status': 200, 'message': 'Location First Received'}
                    # return response

        Response.status = '200'
        response = {'status': 200, 'response': is_tracked, 'message': 'is_tracked'}
        return response
        
    @http.route(version + 'order/get-record-location-data', type='json', auth='public', methods=['Post'], cors="*")
    def get_record_location_data(self, **res):
        req = json.loads(request.httprequest.data)
        order_id = req.get('order_id')
        order_locations = request.env['driver.order.location.data'].sudo().search([('order_id','=',order_id)],order='create_date desc')
        order_location_list=[]
        if order_locations:

            for order_location in order_locations:
                values={
                    'latitude':order_location.latitude,
                    'longitude':order_location.longitude,
                    'location':order_location.location,
                    'date':order_location.create_date

                }
                order_location_list.append(values)

            Response.status = '200'
            response = {'status': 200,'response':order_location_list, 'message': 'Locations List Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Location Found!'}
        return response
        
    # @http.route(version + 'delivery-man/profile', type='json', auth='public', methods=['Post'],cors="*")
    @http.route(version + 'delivery-man/profile', type='json', auth='user', methods=['Post'],cors="*")
    def get_user_profile(self, **res):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if user.partner_id:
            vals = {
                "id":user.id,
                "f_name": user.partner_id.name,
                "l_name": "",
                "phone": user.partner_id.mobile,
                "email": user.partner_id.email,
                "identity_number": "",
                "identity_type": "",
                "identity_image": [],
                "image": "/web/content/" + str(user.partner_id.team_member_image_attachment.id) if user.partner_id.team_member_image_attachment.id else "",
                "password": user.password,
                "created_at": user.create_date,
                "updated_at": user.write_date,
                "auth_token": "",
                "fcm_token": user.user_token if user.user_token else "",
                "branch_id": user.company_id.id,
                "is_active": 1,
                "application_status": "",
                "login_hit_count": 0,
                "is_temp_blocked": 0,
                "temp_block_time": "",
                "central_fcm_token": 0

            }
            Response.status = '200'
            response = {'status':200, 'response': vals, 'message': 'profile Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No profile Found!'}
        return response

    # @http.route(version + 'delivery-man/config', type='json', auth='public', methods=['Post'], cors="*")
    @http.route(version + 'delivery-man/config', type='json', auth='public', methods=['Post'], cors="*")
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
            tax = request.env['account.tax'].sudo().search([],limit=1)
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
                "currency_symbol_en": restaurant_name.currency_id.name  if restaurant_name.currency_id.name else "",
                "currency_id": restaurant_name.currency_id.id,
                "restaurant_logo": "/web/content/" + str(restaurant_name.logo_web_attachment.id) if restaurant_name.logo_web_attachment.id else "",
                "restaurant_logo_dark":"",
                "restaurant_schedule_time": restaurant_schedule_time,
                "restaurant_location_coverage":detail.get_company_zones_witout_id(),
                "minimum_order_value": 1,
                "base_urls": {},
                "tax_percent": amount_tax ,
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
                "currency_symbol_position": "left" if restaurant_name.currency_id.position== "before" else "right",
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
                            "link":  restaurant_name.social_youtube if restaurant_name.social_youtube else "",
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
                "otp_resend_time": 60

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
                    if address!="":
                        address = address + ' , ' + branch.street
                    else:
                        address = branch.street
                if branch.street2:
                    if address!="":
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
                    "zones":detail.get_company_zones_witout_id(branch.id),
                }
                branch_list.append(values)


        return branch_list

    # @http.route(version + 'delivery-man/current-orders', type='json', auth='public', methods=['Post'], cors="*")
    @http.route(version + 'delivery-man/current-orders', type='json', auth='user', methods=['Post'], cors="*")
    def get_current_orders(self):
        driver_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        order_list=[]


        if driver_user:
            driver = driver_user.partner_id
            if driver:
                sale_orders = request.env['sale.order'].sudo().search([('driver_id', '=', driver.id),('sale_order_type', '!=', '3'),('state', '!=', 'cancel'),('order_status', '!=', '7')])
                if sale_orders:
                    for sale_order in sale_orders:
                        order_status = ""
                        if sale_order.order_status == "2":
                            order_status = "Draft"
                        elif sale_order.order_status == "3":
                            order_status = "Confirmed"
                        elif sale_order.order_status == "4":
                            order_status = "In Progress"
                        elif sale_order.order_status == "5":
                            order_status = "Ready"
                        elif sale_order.order_status == "6":
                            order_status = "Out For Delivery"
                        elif sale_order.order_status == "7":
                            order_status = "Delivered"


                        if sale_order.sale_order_type == "1":

                            delivery_product = request.env['product.product'].sudo().search([('is_delivery', '=', True)], limit=1)
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
                            [('partner_id', '=', sale_order.partner_id.id)])
                        if orders:
                            orders_count = len(orders)
                        else:
                            orders_count =0
                        
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
                            "order_status": order_status,
                            "order_time_to_be_ready" : sale_order.order_time_to_be_ready if sale_order.order_time_to_be_ready else None,
                            "assign_time_time" : current_time , #sale_order.assign_time_time if sale_order.assign_time_time else None ,
                            "total_tax_amount": sale_order.amount_tax,
                            "currency_symbol": sale_order.company_id.currency_id.name,
                            "currency_symbol_en": sale_order.company_id.currency_id.name,
                            "payment_method": "cash_on_delivery",
                            "transaction_reference": "",
                            "delivery_address_id": sale_order.partner_shipping_id.id,
                            "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                            "checked": 1,
                            "delivery_man_id": sale_order.driver_id.id if sale_order.driver_id.id else None,
                            "delivery_charge": delivery_charge,
                            "order_note": "",
                            "coupon_code": "",
                            "order_type": "delivery" if sale_order.sale_order_type=="1" else "Pick Up",
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
                            "preparation_time": 0,
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
                                "image": "null",
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
                    
                    if len(order_list)>0:
                        Response.status = '200'
                        response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
                    else:
                        Response.status = '200'
                        response = {'status': 200, 'response': order_list, 'message': 'No Order Found!'}
                else:
                    Response.status = '200'
                    response = {'status': 200, 'response': order_list,'message': 'No data Found!'}

            else:
                Response.status = '200'
                response = {'status': 200, 'response': order_list, 'message': 'Driver Not Found!'}

        else:
            Response.status = '200'
            response = {'status': 200, 'response': order_list, 'message': 'User Not Found!'}

        return response

    # @http.route(version + 'delivery-man/order-details', type='json',   auth='public', methods=['Post','Get'],cors="*")
    @http.route(version + 'delivery-man/order-details', type='json',   auth='public', methods=['Post','Get'],cors="*")
    def get_order_details(self):
        req = json.loads(request.httprequest.data)

        order_id = req.get('order_id')

        Product_Info = ProductInfo()
        order_list = []
        sale_order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
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
                        "sale_order_total":sale_order.amount_total,
                        "id": line.id,
                        "product_id": line.product_id.id,
                        "order_id": order_id,
                        "driver_id":sale_order.driver_id.name if sale_order.driver_id else "",
                        "price": line.price_total,
                        "product_details": {
                            "id": line.product_id.id,
                            "name": line.product_id.name,
                            "description": desc,
                            "image": "/web/content/" + str(
                                line.product_id.image_attachment.id) if line.product_id.image_attachment.id else "",
                            "price": Product_Info.get_product_product_price(line.product_id),
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
                        "preparation_time": line.product_id.preparing_time
                    }
                    order_list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': order_list, 'message': 'Sale Order Details Found'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}


        return response

   

    @http.route(version + 'delivery-man/all-orders', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_orders(self):
        driver_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        order_list = []
        order_list = self.get_orders(driver_user.id)
        if len(order_list):
            Response.status = '200'
            response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
        else:
            Response.status = '200'
            response = {'status': 200, 'response': order_list,'message': 'No data Found!'}

        return response


        

    def get_orders(self,user_id, order_status=None):
        driver_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
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

        if driver_user:
            driver = driver_user.partner_id
            if driver:
                if order_status:
                    sale_orders = request.env['sale.order'].sudo().search([('driver_id', '=', driver.id),('order_status','=',order_status_id)])
                else:
                    sale_orders = request.env['sale.order'].sudo().search([('driver_id', '=', driver.id)])

                if sale_orders:
                    for sale_order in sale_orders:



                        if sale_order.sale_order_type == "1":

                            delivery_product = request.env['product.product'].sudo().search(
                                [('is_delivery', '=', True)], limit=1)
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
                            [('partner_id', '=', sale_order.partner_id.id)])
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
                            "assign_time_time": current_time, #sale_order.assign_time_time if sale_order.assign_time_time else None,
                            "total_tax_amount": sale_order.amount_tax,
                            "currency_symbol": sale_order.company_id.currency_id.name,
                            "currency_symbol_en": sale_order.company_id.currency_id.name,
                            "payment_method": "cash_on_delivery",
                            "transaction_reference": "",
                            "delivery_address_id": sale_order.partner_shipping_id.id,
                            "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                            "checked": 1,
                            "delivery_man_id": sale_order.driver_id.id if sale_order.driver_id.id else None,
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
                            "preparation_time": 0,
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
                                "image": "null",
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



        return order_list
    
    # @http.route('/api/delivery-man/confirm-delivery', type='json', auth='public', methods=['Post'], cors="*")
    @http.route(version + 'delivery-man/confirm-delivery', type='json', auth='user', methods=['Post'], cors="*")
    def confirm_delivery(self):

        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('sale_order_id')
        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            if sale_order:
                sale_order.write(
                    {'order_status': "7"}
                )

                order_trip = request.env['orders.trip'].sudo().search([('order_ids', 'in', sale_order.id)])
                if order_trip:
                    is_delivered = True
                    for inv in order_trip.order_ids:
                        if inv.order_status != '7':
                            is_delivered = False
                    if is_delivered:
                        order_trip.write(
                            {'state': 'arrived'}
                        )
                Response.status = '200'
                response = {'status': 200, 'message': 'Sale Order Delivered!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}

        return response

    # @http.route('/api/delivery-man/update-order-status', type='json', auth='public', methods=['Post'], cors="*")
    @http.route(version + 'delivery-man/update-order-status', type='json', auth='user', methods=['Post'], cors="*")
    def update_order_status(self):

        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('order_id')
        order_status = req.get('status')
        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            if sale_order:
                if order_status =='delivered':
                    order_status_id ='7'
                elif order_status =='out_for_delivery':
                    order_status_id = '6'

                sale_order.write(
                    {'order_status': order_status_id}
                )
                
                # try:
                # order_location = request.env['driver.order.location.data'].sudo().search(
                #     [('order_id', '=', sale_order_id)])
                #
                # if order_location:
                #
                #     if len(order_location) > 0:
                #
                #         saved_location = True
                #     else:
                #         saved_location = False
                # else:
                #     saved_location = False
                #
                # if order_status_id=='6':
                #     if saved_location:
                #         client_user = request.env['res.users'].sudo().search(
                #             [('partner_id', '=', sale_order.partner_id.id)])
                #         if client_user:
                #             notification = Notification
                #             message_name = "قيد الوصول123"
                #
                #             message_description = "الطلبية رقم " + sale_order.name + " أصبحت قيد الوصول"
                #
                #             chat_id = '1'
                #             notification.send_notification(request.env.user, client_user, message_name,
                #                                            message_description,
                #                                            sale_order.id)

                # except:
                #     pass
                
                # if order_status_id=='7':
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
                response = {'status': 200, 'message': 'Sale Order Status Changed!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}

        return response

    @http.route(version + 'delivery-man/update-payment-status', type='json', auth='public', methods=['Post'], cors="*")
    def update_payment_status(self):

        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('order_id')
        payment_status = req.get('status')
        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
            if sale_order:

                sale_order.write(
                    {'payment_status': payment_status}
                )


                Response.status = '200'
                response = {'status': 200, 'message': 'Sale Order Payment Status Changed!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}

        return response
        
    
    @http.route(version + 'delivery-man/update-profile', type='json', auth='user', methods=['Post'], cors="*")
    def update_user_profile(self, **res):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        if user.partner_id:
            # partner = request.env['res.partner'].sudo().search([('id', '=', user.partner_id.id)])
            req = json.loads(request.httprequest.data)
            # order_id = req.get('f_name')

            
            if req.get('name'):
                _name = req.get('name')
                if _name.strip() !='':
                    user_found = request.env['res.users'].sudo().search([('name', '=', _name)])
                    if user != user_found:
                        Response.status =  '401'
                        response = {'status': 401, 'message': 'Duplicated name'}
                        return response

                    user.partner_id.write({
                        "name": _name.strip()
                    })

            # if req.get('phone'):
            #     user.partner_id.write({
            #     "mobile": req.get('phone')
            #     })
            # if req.get('email'):
            #     user.partner_id.write({
            #     "email": req.get('email')
            #     })
            if req.get('image'):
                user.partner_id.write({
                "image_1920": req.get('image')
                })

            Response.status =   200
            response = {'status': 200,  'message': 'profile Updated'}
        else:
            Response.status =   404
            response = {'status': 404, 'message': 'No profile Found!'}
        return response
        
    @http.route(ProductInfo.version + 'delivery-man/message/send/deliveryman', type='json', auth='public', methods=['Post'], cors="*")
    def send_message(self):
        # try:
        req = json.loads(request.httprequest.data)

        # company_id = req.get('company_id')

        driver_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if driver_user:
            images_list = []
            if req.get('images'):
                images_list = req.get('images')

            driver_chat = request.env['driver.chat'].sudo().create({
                "name": req.get('order_id'),
                "message": req.get('message'),
                "image_found": True if len(images_list) > 0 else False,
                "driver_user_id":driver_user.id
            })

            for record in images_list:
                image = request.env['driver.chat.image'].sudo().create({
                    "image": record,
                    "driver_chat_id": driver_chat.id
                })

            Response.status = '200'
            response = {'status': 200, 'message': 'Message Received'}
            
            try:
                order = request.env['sale.order'].sudo().search([('id', '=', req.get('order_id'))])
                chat = request.env['driver.chat'].sudo().search([('name', '=', req.get('order_id'))],limit=1)
                # customer_user = chat.client_user_id
                if chat:
                    customer_user = chat.client_user_id
                    if customer_user==False:
                        partner = order.partner_id
                        customer_user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)])
                else:
                    partner = order.partner_id
                    customer_user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)])


                if customer_user:
                    notification = Notification
                    message_name = "محادثة واردة"

                    message_description = " محادثة واردة متعلقة بالطلبية رقم " + order.name
        
                    chat_id = '1'
                    notification.send_notification(request.env.user, customer_user, message_name, message_description,
                                                   order.id)

            except:
                pass
            
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Driver Not Found'}
        # except:
        #     Response.status = '404'
        #     response = {'status': 404, 'message': 'Error Receiving Message'}

        return response

    @http.route(ProductInfo.version + 'delivery-man/message/send/get-message', type='json', auth='public',
                methods=['Post'], cors="*")
    def get_messages(self):
        req = json.loads(request.httprequest.data)

        order_id = req.get('order_id')
        offset_messages = req.get('offset')
        limit_messages = req.get('limit')
        message_list = []
        driver_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if driver_user:
            messages = request.env['driver.chat'].sudo().search([('name', '=', order_id)],order='create_date Desc', limit=limit_messages,offset = offset_messages*limit_messages)
            # leads = CrmLead.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
            total_size = len(messages)
            beirut_timezone = ProductInfo.beirut_timezone
            for message in messages:
                images=[]
                for image1 in message.images:
                    image_path = "/web/content/" + str(image1.image_attachment.id) if image1.image_attachment.id else ""
                    images.append(image_path)

                if message.client_user_id:
                    client_value={
                        "name":message.client_user_id.partner_id.name,
                        "image": "/web/content/" + str(message.client_user_id.partner_id.team_member_image_attachment.id) if message.client_user_id.partner_id.team_member_image_attachment.id else "",
                    }
                if message.driver_user_id:
                    driver_value={
                        "name":message.driver_user_id.partner_id.name,
                        "image": "/web/content/" + str(message.driver_user_id.partner_id.team_member_image_attachment.id) if message.driver_user_id.partner_id.team_member_image_attachment.id else "",
                    }
                
                create_date_beirut =  message.create_date.astimezone(beirut_timezone)
                
                write_date_beirut = message.write_date.astimezone(beirut_timezone)
                value={
                        "id":message.id,
                        "conversation_id" : message.id,
                        "customer_id":client_value if message.client_user_id else None,
                        "deliveryman_id":driver_value if message.driver_user_id else None,
                        "message":message.message,
                        "attachment": images if len(images)>0 else None,
                        "created_at":create_date_beirut,
                        "updated_at":write_date_beirut,
                }
                message_list.append(value)

            values = {
                        "total_size":total_size,
                        "limit": limit_messages,
                        "offset": offset_messages,
                        "messages": message_list

                    }

            Response.status = '200'
            response = {'status': 200,'response': values, 'message': 'List of Messages'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Driver Not Found'}

        return response

