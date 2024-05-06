from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
import pytz
from datetime import datetime, timedelta
from odoo.addons.das_publicfunction.controller.main import ProductInfo



class EventSaleOrder(http.Controller):
    
    def add_other_address(self,name,mobile):

        partner = request.env['res.partner'].sudo().search([('mobile','=',mobile)],limit=1)
        if partner:
            return partner.id
        else:
            values = {
                "name": name,
                "mobile": mobile,
                "is_client": True,
                "type": 'delivery',


            }

            address = request.env['res.partner'].sudo().create(values)


            return address.id
            
    @http.route(ProductInfo.version + 'place-event', type='json', auth='public', methods=['Post'], cors="*")
    def place_event(self):

        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)

        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])
            if product == False:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response


        company_id = req.get('company_id')

        boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)


        if req.get('user_id'):
            user_id = req.get('user_id')
        else:
            user_id = -1

        if user_id==-1:
            name = req.get('name')
            mobile = req.get('mobile')
            user = boot
            thepartner_id = self.add_other_address(name,mobile)
        else:
            user = request.env['res.users'].sudo().search([('id','=',user_id)])
            thepartner_id = user.partner_id.id

        if user.tz:
            user_timezone = user.tz
        else:
            user_timezone = Product_Info.beirut_timezone

 

        delivery_date_str = req.get('delivery_date')

        date_format = "%d/%m/%Y %H:%M:%S"
        delivery_date = datetime.strptime(delivery_date_str, date_format)

        source_timezone = pytz.timezone('UTC')  # Replace 'UTC' with the actual source timezone

        # Convert the delivery_date from the source timezone to the user_timezone
        # delivery_date = source_timezone.localize(delivery_date).astimezone(pytz.timezone(user_timezone))
        delivery_date = pytz.timezone(user_timezone).localize(delivery_date).astimezone(source_timezone)

        delivery_date_naive = delivery_date.replace(tzinfo=None)

        quotation = request.env['sale.order'].sudo().create({
            "partner_id": thepartner_id,
            "state": 'draft',
            "company_id": company_id,
            "delivery_date": delivery_date_naive,
            "sale_order_type": str(req.get('sale_order_type_id')),
            "partner_shipping_id": thepartner_id,
            "user_id":user.id,
            "event_type":req.get('event_type') if req.get('event_type')  else "",
            "note":req.get('note') if req.get('note')  else ""
            # "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
        })
        
        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])

            price = product.lst_price
            attribute_values_list = []
            attribute_values_list = record['attribute_values']
            attribute_value_name = ''
            attribute_value_name_ar = ''
            if attribute_values_list:

                for attribute_value_id in attribute_values_list:
                    attribute_value = request.env['product.attribute.value'].sudo().search(
                        [('id', '=', attribute_value_id)])

                    attribute_name = attribute_value.attribute_id.name
                    if attribute_value_name == '':
                        attribute_value_name = attribute_name + '(' + attribute_value.name + ')'
                    else:
                        attribute_value_name = attribute_value_name + ',' + attribute_name + '(' + attribute_value.name + ')'

                for attribute_value_id in attribute_values_list:
                    attribute_value = request.env['product.attribute.value'].with_context(lang='ar_001').sudo().search(
                        [('id', '=', attribute_value_id)])

                    attribute_name = attribute_value.attribute_id.name
                    if attribute_value_name == '':
                        attribute_value_name_ar = attribute_name + '(' + attribute_value.name + ')'
                    else:
                        attribute_value_name_ar = attribute_value_name_ar + ',' + attribute_name + '(' + attribute_value.name + ')'


            if product:
                sale_order_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name ,
                    "price_unit": price ,
                    # "price_total": record['totlal_price_product'],
                    "notes": record['notes'],

                    "image_found":True if len(record['images'])>0 else False
                    # "price_unit": self.get_promo_price(product.id)
                })
                sale_order_line.with_context(lang='ar_001').update(
                    {'kitchen_notes': attribute_value_name_ar})
                sale_order_line.update({'kitchen_notes': attribute_value_name})

                for record in record['images']:
                    image = request.env['order.line.image'].sudo().create({
                        "image": record,
                        "order_line_id": sale_order_line.id
                    })
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response





        Response.status = '200'
        response = {'status': 200, 'message': 'Event Received'}

        return response

    def place_event_old(self):

        req = json.loads(request.httprequest.data)

        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])
            if product == False:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response
            addons = []
            addons = record['addons_note']
            addon_price = 0
            if addons:
                addon_price = 0
                for addon in addons:

                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])
                    if product_addon == False:
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Add Not Found'}
                        return response

        company_id = req.get('company_id')

        boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

        if req.get('user_id'):
            user_id = req.get('user_id')
            if user_id == -1:
                name = req.get('name')
                mobile = req.get('mobile')
                user = boot
                thepartner_id = self.add_other_address(name, mobile)
            else:
                user = request.env['res.users'].sudo().search([('id', '=', user_id)])
                thepartner_id = user.partner_id.id

        user_timezone = user.tz

        delivery_date_str = req.get('delivery_date')

        date_format = "%d/%m/%Y %H:%M:%S"
        delivery_date = datetime.strptime(delivery_date_str, date_format)

        source_timezone = pytz.timezone('UTC')  # Replace 'UTC' with the actual source timezone

        # Convert the delivery_date from the source timezone to the user_timezone
        # delivery_date = source_timezone.localize(delivery_date).astimezone(pytz.timezone(user_timezone))
        delivery_date = pytz.timezone(user_timezone).localize(delivery_date).astimezone(source_timezone)

        delivery_date_naive = delivery_date.replace(tzinfo=None)

        quotation = request.env['sale.order'].sudo().create({
            "partner_id": thepartner_id,
            "state": 'draft',
            "company_id": company_id,
            "delivery_date": delivery_date_naive,
            "sale_order_type": req.get('sale_order_type_id'),
            "partner_shipping_id": thepartner_id,
            "user_id": user.id,
            "event_type": req.get('event_type') if req.get('event_type') else "",
            "note": req.get('note') if req.get('note') else ""
            # "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
        })

        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])

            price = product.lst_price
            addons = record['addons_note']
            addon_price = 0
            notes_addon = ""
            if addons:
                addon_price = 0
                for addon in addons:
                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])

                    # addon_price = addon_price + addon['price']
                    price = price + product_addon.lst_price
                    notes_addon = notes_addon + product_addon.name
            if product:
                sale_order_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    "price_unit": price,
                    # "price_total": record['totlal_price_product'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    "image_found": True if len(record['images']) > 0 else False
                    # "price_unit": self.get_promo_price(product.id)
                })
                for record in record['images']:
                    image = request.env['order.line.image'].sudo().create({
                        "image": record,
                        "order_line_id": sale_order_line.id
                    })
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response

        Response.status = '200'
        response = {'status': 200, 'message': 'Event Received'}

        return response

    @http.route(ProductInfo.version + 'events-history', type='json', auth='public', methods=['Post'], cors='*')
    def get_events_orders(self):
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if retailer_user:

            if lang == "ar":
                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('sale_order_type', '=', '3')],
                    order='create_date Desc')
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('sale_order_type', '=', '3')],
                    order='create_date Desc')

            orders = []

            if lang == "ar":
                order_status = "مناسبة"
            else:
                order_status = "Event"

            delivery_product = request.env['product.product'].sudo().search(
                [('is_delivery', '=', True)], limit=1)

            if quotations:
                for order in quotations:
                    delivery_charge = 0
                    products = []
                    for line in order.order_line:

                        try:
                            the_notes = line.kitchen_notes
                        except:
                            the_notes = line.notes

                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": line.notes if line.notes else "",
                                "kitchen_notes": line.kitchen_notes if line.kitchen_notes else "",
                                "product_image": "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment else "",
                                "quantity": int(line.product_uom_qty),
                                "price": 0.0
                            }
                            products.append(values)

                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id": order.sale_order_type,
                            "delivery_fees": delivery_charge,
                            "order_date": order.date_order.date(),
                            "amount": 0.0,
                            "note": order.note if order.note else "",
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": "7",
                            "products": products
                        }
                    )
                Response.status  = '200'
                response = {'status': 200, 'response': orders, 'message': 'list of events found'}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'no events found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User not found'}
        return response

    @http.route(ProductInfo.version + 'events-history-http', type='http', auth='public', methods=['Get'], cors='*')
    def get_events_orders_http(self):
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if retailer_user:

            if lang == "ar":
                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('sale_order_type', '=', '3')],
                    order='create_date Desc')
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('sale_order_type', '=', '3')],
                    order='create_date Desc')

            orders = []

            if lang == "ar":
                order_status = "مناسبة"
            else:
                order_status = "Event"

            delivery_product = request.env['product.product'].sudo().search(
                [('is_delivery', '=', True)], limit=1)

            if quotations:
                for order in quotations:
                    delivery_charge = 0
                    products = []
                    for line in order.order_line:



                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": line.notes if line.notes else "",
                                "kitchen_notes": line.kitchen_notes if line.kitchen_notes else "",
                                "product_image": "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment else "",
                                "quantity": int(line.product_uom_qty),
                                "price": 0.0
                            }
                            products.append(values)
                    order_date = order.date_order.date()
                    order_datetime = order_date.strftime('%Y-%m-%d')
                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id": order.sale_order_type,
                            "delivery_fees": delivery_charge,
                            "order_date": order_datetime,
                            "amount": 0.0,
                            "note": order.note if order.note else "",
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": "7",
                            "products": products
                        }
                    )
                Response.status  = '200'
                response = {'status': 200, 'response': orders, 'message': 'list of events found'}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'no events found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User not found'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'current-event-details', type='json', auth='public', methods=['Post'], cors='*')
    def get_current_event_details(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        order_id = req.get('order_id')
        if retailer_user:
            # sale_orders_delivered = quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],order='create_date Desc')

            # quotations = request.env['sale.order'].sudo().search(
            #     [('id', '=', order_id)])

            if lang == "ar":

                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search(
                    [('id', '=', order_id)])
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('id', '=', order_id)])

            orders = []

            delivery_product = request.env['product.product'].sudo().search(
                [('is_delivery', '=', True)], limit=1)

            if quotations:
                for order in quotations:
                    order_location = request.env['driver.order.location.data'].sudo().search(
                        [('order_id', '=', order.id)])

                    if order_location:

                        if len(order_location) > 0:

                            saved_location = True
                        else:
                            saved_location = False
                    else:
                        saved_location = False

                    order_status = ""
                    if order.order_status == "2":
                        if lang == "ar":
                            order_status = "مسودة"
                        else:
                            order_status = "Draft"
                    elif order.order_status == "3":
                        if lang == "ar":
                            order_status = "مؤكدة"
                        else:
                            order_status = "Confirmed"

                    elif order.order_status == "4":
                        if lang == "ar":
                            order_status = "قيد التحضير"
                        else:
                            order_status = "In Progress"

                    elif order.order_status == "5":
                        if lang == "ar":
                            order_status = "جاهزة"
                        else:
                            order_status = "Ready"

                    elif order.order_status == "6":
                        if lang == "ar":
                            order_status = "قيد التوصيل"
                        else:
                            order_status = "Out For Delivery"

                    elif order.order_status == "7":
                        if lang == "ar":
                            order_status = "تم التوصيل"
                        else:
                            order_status = "Delivered"

                    order_status_id = order.order_status
                    if saved_location == False:
                        if order.order_status == '5' or order.order_status == '6':
                            order_status_id = "4"
                            order_status = "In Progress"

                    products = []
                    delivery_charge = 0
                    for line in order.order_line:
                        if order.sale_order_type == "1":

                            if delivery_product.id == line.product_id.id:
                                delivery_charge = line.price_total
                        else:
                            delivery_charge = 0

                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": line.notes if line.notes else "",
                                "kitchen_notes": line.kitchen_notes if line.kitchen_notes else "",
                                "product_image": base_url + "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total / int(line.product_uom_qty), 2)
                            }
                            products.append(values)
                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id": order.sale_order_type,
                            "delivery_fees": delivery_charge,
                            "order_date": order.date_order.astimezone(
                                ProductInfo.beirut_timezone).date(),
                            "event_date": order.delivery_date.astimezone(
                                ProductInfo.beirut_timezone).date() if order.delivery_date else None,
                            "event_time": order.delivery_date.astimezone(
                                ProductInfo.beirut_timezone).time() if order.delivery_date else None,
                            "amount": order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": order_status_id,
                            "event_type": order.event_type if order.event_type  else "",
                            "note": order.note if order.note  else "",
                            "products": products
                        }
                    )
                Response.status = '200'
                response = {'status': 200, 'response': orders[0], 'message': 'Details of event found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'no event found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User not found'}
        return response