import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re

from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification

class ChefsAPI(http.Controller):

    version = ProductInfo.version

    @http.route(version + 'kitchen/current-orders', type='json', auth='user', methods=['Post', 'Get'], cors="*")
    def get_kitchen_current_orders(self):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if user:
            kitchen_id = user.partner_id.kitchen_id
            if kitchen_id:
                order_list = self.get_kitchen_orders(user.company_id, kitchen_id )

                if len(order_list):
                    Response.status = '200'
                    response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
                else:
                    Response.status = '200'
                    response = {'status': 200,'response': order_list, 'message': 'No data Found!'}
            else:
                Response.status = '200'
                response = {'status': 200,'response': [], 'message': 'Kitchen Not Found!'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': [], 'message': 'User Not Found!'}
        return response

    @http.route(version + 'kitchen/completed-orders', type='json', auth='user', methods=['Post', 'Get'], cors="*")
    def get_kitchen_history_orders(self):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        req = json.loads(request.httprequest.data)

        limit = req.get('limit')
        offset = req.get('offset')
        if user:
            kitchen_id = user.partner_id.kitchen_id
            if kitchen_id:
                order_list = self.get_kitchen_orders_completed(user.company_id, kitchen_id ,limit,offset)

                if len(order_list):
                    Response.status = '200'
                    response = {'status': 200, 'response': order_list, 'message': 'Sale Orders Found'}
                else:
                    Response.status = '200'
                    response = {'status': 200,'response': order_list, 'message': 'No data Found!'}
            else:
                Response.status = '200'
                response = {'status': 200,'response': [], 'message': 'Kitchen Not Found!'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': [], 'message': 'User Not Found!'}
        return response

    def get_kitchen_orders_completed(self, company_id, kitchen_id,limit,offset):

        order_list = []

        detail = ProductInfo()
        if company_id:
            sale_orders = request.env['digitile.order.kitchen'].sudo().search(
                    [('state', '!=', 'cancel'), ('company_id', '=', company_id.id), ('sale_order_type', 'in', [1, 2]),
                     ('order_status', '=', '5')], order='create_date Desc',limit=limit,offset=limit*offset)
            #
            #

            if sale_orders:
                delivery_product = request.env['product.product'].sudo().search(
                    [('is_delivery', '=', True)], limit=1)
                for sale_order in sale_orders:
                    product_list = []
                    order_lines = request.env['digitile.order.kitchen.line'].sudo().search(
                        [('order_kitchen_id', '=', sale_order.id)])
                    add_product = False
                    for line in order_lines:

                        product = line.product_id
                        if product!=delivery_product:
                            if product.kitchen_id:
                                if product.kitchen_id == kitchen_id:
                                    add_product = True
                                    break
                                # else:
                                #     add_product = False
                            else:
                                if kitchen_id.default_kitchen:
                                    add_product = True
                                    break
                                # else:
                                #     add_product = False

                    if add_product:
                            # product_list.append(values)
                        address = ""
                        orders_count = 0
                        if sale_order.order_status == "2":
                            theorder_status_id = "Draft"
                        elif sale_order.order_status == "3":
                            theorder_status_id = "Confirmed"
                        elif sale_order.order_status == "4":
                            theorder_status_id = "In Progress"
                        elif sale_order.order_status == "5":
                            theorder_status_id = "Ready"
                        preparation_time = 0  # detail.get_preparation_time(sale_order)
                        if preparation_time == 0:
                            preparation_time_str = "0"
                        else:
                            preparation_time_str = str(preparation_time)
                        values = {
                            "id": sale_order.id,
                            "name": sale_order.name,
                            "user_id": None,
                            "order_amount": 0.0,
                            "coupon_discount_amount": 0,
                            "coupon_discount_title": "",
                            "payment_status": "unpaid",
                            "order_status": theorder_status_id,
                            "order_time_to_be_ready": None,
                            "assign_time_time": None,
                            "total_tax_amount": 0.0,
                            "payment_method": "cash_on_delivery",
                            "transaction_reference": "",
                            "delivery_address_id": None,
                            "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                            "checked": 1,
                            "delivery_man_id": None,
                            "delivery_charge": 0.0,
                            "order_note": "",
                            "coupon_code": "",
                            "order_type": "",
                            "branch_id": 1,
                            "callback": "",
                            "delivery_date": None,
                            "delivery_time": None,
                            # "delivery_date_n": sale_order.delivery_date.astimezone(
                            #     ProductInfo.beirut_timezone).date() if sale_order.delivery_date else None,
                            # "delivery_time_n": sale_order.delivery_date.astimezone(
                            #     ProductInfo.beirut_timezone).time() if sale_order.delivery_date else None,
                            "extra_discount": "0.00",
                            "delivery_address": {
                                "id": None,
                                "address_type": None,
                                "contact_person_number": "",
                                "floor": "",
                                "house": "",
                                "road": "",
                                "address": address,
                                "latitude": None,
                                "longitude": None,
                                "created_at": None,
                                "updated_at": None,
                                "user_id": None,
                                "contact_person_name": None
                            },
                            "preparation_time": preparation_time_str,
                            "table_id": "",
                            "number_of_people": "",
                            "table_order_id": "",

                            "customer": {
                                "id": None,
                                "f_name": None,
                                "l_name": "",
                                "email": "",
                                "user_type": "",
                                "is_active": 1,
                                "image": " ",
                                "is_phone_verified": 0,
                                "email_verified_at": "",
                                "created_at": None,
                                "updated_at": None,
                                "email_verification_token": "",
                                "phone": "",
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
                                "orders_count": None

                            }
                        }
                        order_list.append(values)

        returnvalues = {
            "list": order_list,
            "total_size": len(sale_orders) if sale_orders else 0,
            "limit": limit,
            "offset": offset
        }
        return returnvalues

    def get_kitchen_orders(self, company_id, kitchen_id):

        order_list = []

        detail = ProductInfo()
        if company_id:
            sale_orders = request.env['digitile.order.kitchen'].sudo().search(
                    [('state', '!=', 'cancel'), ('company_id', '=', company_id.id), ('sale_order_type', 'in', [1, 2]),
                     ('order_status', 'in', ['3', '4','5'])], order='create_date Desc')


            if sale_orders:
                delivery_product = request.env['product.product'].sudo().search(
                    [('is_delivery', '=', True)], limit=1)
                for sale_order in sale_orders:
                    product_list = []
                    order_lines = request.env['digitile.order.kitchen.line'].sudo().search(
                        [('order_kitchen_id', '=', sale_order.id)])
                    add_product = False
                    for line in order_lines:
                        
                        product = line.product_id
                        if product!=delivery_product:
                            if product.kitchen_id:
                                if product.kitchen_id == kitchen_id:
                                    add_product = True
                                    break
                                # else:
                                #     add_product = False
                            else:
                                if kitchen_id.default_kitchen:
                                    add_product = True
                                    break
                                # else:
                                #     add_product = False

                    if add_product:
                            # product_list.append(values)
                        address = ""
                        orders_count = 0
                        if sale_order.order_status == "2":
                            theorder_status_id = "Draft"
                        elif sale_order.order_status == "3":
                            theorder_status_id = "Confirmed"
                        elif sale_order.order_status == "4":
                            theorder_status_id = "In Progress"
                        elif sale_order.order_status == "5":
                            theorder_status_id = "Ready"
                        preparation_time = 0  # detail.get_preparation_time(sale_order)
                        if preparation_time == 0:
                            preparation_time_str = "0"
                        else:
                            preparation_time_str = str(preparation_time)
                        values = {
                            "id": sale_order.id,
                            "name": sale_order.name,
                            "user_id": None,
                            "order_amount": 0.0,
                            "coupon_discount_amount": 0,
                            "coupon_discount_title": "",
                            "payment_status": "unpaid",
                            "order_status": theorder_status_id,
                            "order_time_to_be_ready": None,
                            "assign_time_time": None,
                            "total_tax_amount": 0.0,
                            "payment_method": "cash_on_delivery",
                            "transaction_reference": "",
                            "delivery_address_id": None,
                            "created_at": sale_order.create_date.astimezone(ProductInfo.beirut_timezone),
                            "updated_at": sale_order.write_date.astimezone(ProductInfo.beirut_timezone),
                            "checked": 1,
                            "delivery_man_id": None,
                            "delivery_charge": 0.0,
                            "order_note": "",
                            "coupon_code": "",
                            "order_type": "",
                            "branch_id": 1,
                            "callback": "",
                            # "delivery_date": None,
                            # "delivery_time":None,
                            "delivery_date": sale_order.delivery_date.astimezone(
                                ProductInfo.beirut_timezone).date() if sale_order.delivery_date else None,
                            "delivery_time": sale_order.delivery_date.astimezone(
                                ProductInfo.beirut_timezone).time() if sale_order.delivery_date else None,
                            "extra_discount": "0.00",
                            "delivery_address": {
                                "id": None,
                                "address_type": None,
                                "contact_person_number": "",
                                "floor": "",
                                "house": "",
                                "road": "",
                                "address": address,
                                "latitude": None,
                                "longitude": None,
                                "created_at": None,
                                "updated_at": None,
                                "user_id": None,
                                "contact_person_name": None
                            },
                            "preparation_time": preparation_time_str,
                            "table_id": "",
                            "number_of_people": "",
                            "table_order_id": "",

                            "customer": {
                                "id": None,
                                "f_name": None,
                                "l_name": "",
                                "email": "",
                                "user_type": "",
                                "is_active": 1,
                                "image": " ",
                                "is_phone_verified": 0,
                                "email_verified_at": "",
                                "created_at": None,
                                "updated_at": None,
                                "email_verification_token": "",
                                "phone": "",
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
                                "orders_count": None

                            }
                        }
                        order_list.append(values)

        return order_list


    @http.route(version + 'kitchen/order-details', type='json', auth='user', methods=['Post', 'Get'],
                cors="*")
    def get_order_details(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        order_id = req.get('order_id')
        kitchen_id = req.get('kitchen_id')
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        req = json.loads(request.httprequest.data)
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        Product_Info = ProductInfo()
        order_list = []
        sale_order  = request.env['digitile.order.kitchen'].sudo().search(
            [('id', '=', order_id)])
        if kitchen_id==False:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Kitchen!'}
            return response
        kitchen = request.env['digitile.kitchen'].sudo().search([('id','=',kitchen_id)])
        if kitchen == False:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Kitchen!'}
            return response
        if user:
            if sale_order:
                delivery_product = request.env['product.product'].sudo().search(
                        [('is_delivery', '=', True)], limit=1)
                # order_lines = request.env['digitile.order.kitchen.line'].sudo().search(
                #     [('order_kitchen_id', '=', sale_order.id)])

                if lang == 'ar':
                    order_lines = request.env['digitile.order.kitchen.line'].with_context(lang='ar_001').sudo().search(
                        [('order_kitchen_id', '=', sale_order.id)])
                else:
                    order_lines = request.env['digitile.order.kitchen.line'].sudo().search(
                        [('order_kitchen_id', '=', sale_order.id)])

                for line in order_lines:
                    add_product = False
                    # product = request.env['product.product'].sudo().search([('id','=',)])
                    

                    try:
                        the_notes = line.kitchen_notes

                    except:
                        the_notes = line.notes
                    if delivery_product.id != line.product_id.id:
                        product = line.product_id

                        if product.kitchen_id:
                            if product.kitchen_id.id == kitchen_id:
                                add_product = True

                            # else:
                            #     add_product = False
                        else:

                            if kitchen.default_kitchen:
                                add_product = True

                        if add_product:
                            if line.product_id.description:
                                desc = re.sub(r'<.*?>', ' ', line.product_id.description)
                            else:
                                desc = ''
                            desc = desc.strip()


                            amount = 0.0

                            if line.order_status == "2":
                                theorder_status_id = "Draft"
                            elif line.order_status == "3":
                                theorder_status_id = "Confirmed"
                            elif line.order_status == "4":
                                theorder_status_id = "In Progress"
                            elif line.order_status == "5":
                                theorder_status_id = "Ready"
                            # ("10", "10 mins"),
                            # ("20", "20 mins"),
                            # ("30", "30 mins"),
                            # ("40", "40 mins"),
                            # ("50", "50 mins"),
                            # ("60", "60 mins"),
                            # ("70", "70 mins"),
                            # ("80", "80 mins"),
                            # ("90", "90 mins"),
                            # ("100", "100 mins"),
                            # ("110", "110 mins"),
                            # ("120", "120 mins"),
                            if line.product_id.preparing_time:
                                preparing_time= line.product_id.preparing_time
                            else:
                                preparing_time="0"
                            values = {

                                "id": line.id,
                                "product_id": line.product_id.id,
                                "order_id": order_id,
                                "price": 0.0,
                                "order_status":theorder_status_id,
                                "product_details": {
                                    "id": line.product_id.id,
                                    "name": line.product_id.name,
                                    "description": desc,
                                    "notes": the_notes,
                                    "image": "/web/content/" + str(
                                        line.product_id.image_attachment.id) if line.product_id.image_attachment.id else "",
                                    # "price": Product_Info.get_product_product_price(line.product_id),
                                    "price": 0.0,
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
                                "quantity": line.qtity,
                                "tax_amount": 0.0,
                                "created_at": line.create_date.astimezone(ProductInfo.beirut_timezone),
                                "updated_at": line.write_date.astimezone(ProductInfo.beirut_timezone),
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
                                "delivery_time":  None,
                                "delivery_date":  None,
                                "preparation_time": preparing_time,
                                "add_ons": None,
                                "item_details": None
                            }
                            order_list.append(values)
                        deliveryman = {}

                Response.status = '200'
                response = {'status': 200, 'details': order_list, 'deliveryman': deliveryman,
                                'message': 'Sale Order Details Found'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'No data Found!'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}

        return response

    @http.route(version + 'kitchen/update-order-detail-status', type='json', auth='user', methods=['Post'],
                cors="*")
    def update_order_status(self):

        req = json.loads(request.httprequest.data)
        order_detail_id = req.get('order_detail_id')
        order_status = req.get('status')
        if order_detail_id:
            sale_order_detail = request.env['digitile.order.kitchen.line'].sudo().search([('id', '=', order_detail_id)])
            if sale_order_detail:
                if order_status == 'ready':
                    order_status_id = '5'
                # elif order_status == 'in_progress':
                #     order_status_id = '4'
                # elif order_status == 'confirmed':
                #     order_status_id = '3'

                    sale_order_detail.write(
                        {'order_status': order_status_id}
                    )
                    if sale_order_detail.model_type == 'sale':
                        order_detail = request.env['sale.order.line'].sudo().search([('id', '=', sale_order_detail.model_id)])
                        if order_detail:
                            order_detail.write(
                                {'order_status': order_status_id}
                            )
                            #لقد لغيت هذه الرسالة لأنها مزعجة للمدير ولكن يجب تشغيلها في حالة ال
                            #dine in
                            # order = order_detail.order_id
                            # notification = Notification
                            # message_name = "تجهيز صنف"
    
                            # message_description = "لقد تم تجهيز الصنف " + order_detail.product_id.name + "التابع للطلبية رقم " + order.name
    
                            # chat_id = '1'
                            
                            # managers = request.env['res.partner'].sudo().search(
                            #     [('is_manager', '=', 'True'), ('company_id', '=', order.company_id.id)])
                            
                            # for manager in managers:
                            #     manager_user = request.env['res.users'].sudo().search(
                            #     [('partner_id', '=', manager.id)])
                            #     if manager_user:
                            #         notification.send_notification(request.env.user, manager_user, message_name,
                            #                                   message_description,
                            #                                       order.id)
                            
                            
                    Response.status = '200'
                    response = {'status': 200, 'message': 'Order Detail Status Changed!'}
                    try:
                        order_kitchen_id = sale_order_detail.order_kitchen_id
                        order_kitchen = request.env['digitile.order.kitchen'].sudo().search([('id','=',order_kitchen_id)])
                        
                        delivery_product = request.env['product.product'].sudo().search(
                            [('is_delivery', '=', True)], limit=1)
                        if order_kitchen.model_type=='sale':
                            sale_order = request.env['sale.order'].sudo().search([('id','=',order_kitchen.model_id)])
                            
                            if sale_order:
                                ready = True
                                for line in sale_order.order_line:
                                    if delivery_product !=line.product_id:
                                        if line.order_status!='5':
                                            ready = False
                                            break

                                if ready:
                                    sale_order.write(
                                        {'order_status': order_status_id}
                                    )

                    except:
                        pass
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Order Status Not Found!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Order Detail Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Order Detail Not Found!'}

        return response