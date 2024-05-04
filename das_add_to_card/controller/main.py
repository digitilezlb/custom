from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
import logging
from datetime import date, datetime
import requests

from datetime import datetime, timedelta
import pytz
# from odoo.addons.smile_log.tools import SmileDBLogger
from odoo.addons.das_publicfunction.controller.main import ProductInfo

from odoo.addons.das_first_order.controller.main import FirstOrderDiscount

from odoo.addons.web.models.ir_http import Http
from odoo.addons.das_user_notification.controller.main import Notification


class AddToCardController(http.Controller):

    def check_prices(self, product, addons, price_unit):

        Product_Info = ProductInfo()

        if product.app_publish == True:

            addon_price = 0
            if addons:
                addon_price = 0
                for addon in addons:

                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])
                    if len(product_addon) == 0:
                        response = {'status': 404, 'message': 'Add On Not Found', 'add_on_id': addon['product_id']}
                        return response

                    try:
                        res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                        included = res['total_included']
                        price_product = included
                    except:
                        price_product = product_addon.lst_price

                    price_without_TVA = Product_Info.get_product_product_price(product_addon)
                    if addon['price'] != price_without_TVA:
                        Response.status = '404'
                        values = Product_Info.get_product_product_details(product_addon)
                        response = {'status': 404, 'message': 'Add On Price Not Correct',
                                    'product_id': addon['product_id'], 'product_name': product_addon.name,
                                    'final_price_Without_TVA': values['final_price_Without_TVA'],
                                    'final_price': values['final_price']}
                        return response
                    addon_price = addon_price + addon['price']

            # price_unit = record['price']

            try:
                res = product.taxes_id.compute_all(product.lst_price, product=product)
                included = res['total_included']
                price_product = included
            except:
                price_product = product.lst_price

            price_product_without_tva = round(Product_Info.get_product_product_price(product), 3)

            if round((price_unit - addon_price), 3) != price_product_without_tva:
                Response.status = '404'
                values = Product_Info.get_product_product_details(product)
                response = {'status': 404, 'message': 'Price Not Correct',
                            'product_id': product.id, 'product_name': product.name,
                            'final_price_Without_TVA': values['final_price_Without_TVA'],
                            'final_price': values['final_price']}
                return response

            response = {'status': 200}
            return response
        else:

            response = {'status': 404, 'message': 'Product Not Available', 'product_id': product.id,
                        'product_name': product.name}
            return response

    @http.route(ProductInfo.version + 'place-order-user-new', type='json', auth='public', methods=['Post'], cors="*")
    def place_order_user_new(self):
        Product_Info = ProductInfo()

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        zone_id = req.get('zone_id')
        discount = 0.0
        try:
            discount = req.get('discount')
            if not discount:
                discount = 0.0
        except:
            discount = 0.0

        company_id = req.get('company_id')
        if company_id:
            company = request.env['res.company'].sudo().search(
                [('id', '=', company_id)])
            try:
                if company.disable_users:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Users Disabled'}
                    return response
            except:
                pass
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Company is required'}
            return response

        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if not user:
            Response.status = '404'

            response = {'status': 404, 'message': 'User Not Found'}
            return response

        user_timezone = user.tz

        delivery_date_str = req.get('delivery_date')

        date_format = "%d/%m/%Y %H:%M:%S"
        delivery_date = datetime.strptime(delivery_date_str, date_format)

        source_timezone = pytz.timezone('UTC')  # Replace 'UTC' with the actual source timezone

        # Convert the delivery_date from the source timezone to the user_timezone
        # delivery_date = source_timezone.localize(delivery_date).astimezone(pytz.timezone(user_timezone))
        delivery_date = pytz.timezone(user_timezone).localize(delivery_date).astimezone(source_timezone)

        delivery_date_naive = delivery_date.replace(tzinfo=None)

        # retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        # if req.get('sale_order_type_id')=='1':
        if req.get('sale_order_type_id') == '1':
            thepartner_id = req.get('address_id')
        else:
            thepartner_id = user.partner_id.id

        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', user.partner_id.id), ('state', '=', 'draft'),
             ('sale_order_type','in',['1','2']),('user_place_order', '=', False)])

        if not quotation:
            Response.status = '404'

            response = {'status': 404, 'message': 'Quotation Not Found'}
            return response

        try:
            value = {
                "company_id": company_id,
                "delivery_date": delivery_date_naive,
                "sale_order_type": req.get('sale_order_type_id'),
                "partner_shipping_id": thepartner_id,
                "user_id": user.id,
                "zone_id": zone_id,
                "discount_type": "percent",
                "discount_rate": discount,
                "user_place_order": True
            }
        except:
            value = {

                "company_id": company_id,
                "delivery_date": delivery_date_naive,
                "sale_order_type": req.get('sale_order_type_id'),
                "partner_shipping_id": thepartner_id,
                "user_id": user.id,
                "zone_id": zone_id,
                "user_place_order": True
            }
        quotation.sudo().update(value)
        quotation.supply_rate()
        if req.get('sale_order_type_id') == '1':
            delivery_fees = req.get('delivery_fees')
            delivery_product = request.env['product.product'].sudo().search([('is_delivery', '=', True)], limit=1)
            if delivery_product:
                request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": delivery_product.id,
                    "product_uom_qty": 1,
                    'name': delivery_product.name,
                    "price_unit": delivery_fees,
                    # "price_unit": self.get_promo_price(product.id)
                })

        Response.status = '200'
        response = {'status': 200, 'message': 'Order Received'}

        # try:
        notification = Notification
        message_name = "اضافة طلبية"

        message_description = "لقد تم اضافة الطلبية رقم " + quotation.name

        chat_id = '1'

        managers = request.env['res.partner'].sudo().search(
            [('is_manager', '=', 'True'), ('company_id', '=', company_id)])
        if managers:
            for manager in managers:
                manager_user = request.env['res.users'].sudo().search([('partner_id', '=', manager.id)])
                if manager_user:
                    notification.send_notification(request.env.user, manager_user, message_name, message_description,
                                                   quotation.id)

        # except:
        #     pass
        return response

    @http.route(ProductInfo.version + 'add-cart-item', type='json', auth='public', methods=['Post'], cors="*")
    def add_products_to_card(self):
        Product_Info = ProductInfo()
        order_line = []
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        company_id = req.get('company_id')

        x_localization = request.httprequest.headers.get('x-localization')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        lang = "en"

        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('company_id', '=', company_id), ('state', '=', 'draft'),
             ('sale_order_type', 'in', ['1', '2']), ('user_place_order', '=', False)])



        if not quotation:
            quotation = request.env['sale.order'].sudo().create({
                "partner_id": retailer_user.partner_id.id,
                "state": 'draft',
                "user_place_order": False,
                'company_id': company_id

            })

        if not req.get('products'):
            Response.status = '404'
            response = {'status': 404, 'message': 'Products is required'}
            return response
        # try:
        if not isinstance(req.get('products'), list):
            Response.status = '404'
            response = {'status': 404, 'message': 'Products must be list'}
            return response
        if len(req.get('products')) == 0:
            Response.status = '404'
            response = {'status': 404, 'message': 'Products is required'}
            return response
        # except:
        #     Response.status = '404'
        #     response = {'status': 404, 'message': 'Products is required'}
        #     return response

        kitchen_notes = ""
        kitchen_notes_ar = ""
        kitchen_notes_en = ""

        for record in req.get('products'):

            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])
            if len(product) == 0:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found', 'product_id': record['product_id']}
                return response
            # the_check_response = self.check_prices(product, record['addons_note'], record['price'])
            # if the_check_response['status'] != 200:
            #     Response.status = the_check_response['status']
            #     response = the_check_response
            #     return response

            if product.app_publish == True:

                addon_price = 0
                addons = record['addons_note']
                if addons:
                    addon_price = 0
                    for addon in addons:

                        product_addon = request.env['product.product'].sudo().search(
                            [('id', '=', addon['product_id'])])
                        if len(product_addon) == 0:
                            Response.status = '404'
                            response = {'status': 404, 'message': 'Add On Not Found', 'add_on_id': addon['product_id']}
                            return response

                        try:
                            res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = product_addon.lst_price

                        price_without_TVA = Product_Info.get_product_product_price(product_addon)
                        if addon['price'] != price_without_TVA:
                            Response.status = '404'
                            values = Product_Info.get_product_product_details(product_addon)
                            response = {'status': 404, 'message': 'Add On Price Not Correct',
                                        'product_id': addon['product_id'], 'product_name': product_addon.name,
                                        'final_price_Without_TVA': values['final_price_Without_TVA'],
                                        'final_price': values['final_price']}
                            return response
                        addon_price = addon_price + addon['price']

                # price_unit = record['price']

                try:
                    res = product.taxes_id.compute_all(product.lst_price, product=product)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = product.lst_price

                price_product_without_tva = round(Product_Info.get_product_product_price(product), 3)

                if round((record['price'] - addon_price), 3) != price_product_without_tva:
                    Response.status = '404'
                    values = Product_Info.get_product_product_details(product)
                    response = {'status': 404, 'message': 'Price Not Correct',
                                'product_id': product.id, 'product_name': product.name,
                                'final_price_Without_TVA': values['final_price_Without_TVA'],
                                'final_price': values['final_price']}
                    return response
                # Response.status = '200'
                # response = {'status': 200}
                # return response
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Available', 'product_id': product.id,
                            'product_name': product.name}
                return response

            kitchen_notes_ar = Product_Info.create_kitchen_notes_new(
                record['notes'], record['addons_note'], record['removable_ingredients_note'],
                record['combo_content'], "ar",product)
            kitchen_notes_en = Product_Info.create_kitchen_notes_new(
                record['notes'], record['addons_note'], record['removable_ingredients_note'],
                record['combo_content'], "en",product)
            # if quotation:
            exist = False
            for line in quotation.order_line:
                exist = False
                exist_note = False
                exist_addons_note = False
                exist_remove_note = False
                if line.notes:
                    if line.notes == record['notes']:
                        exist_note = True
                else:
                    if len(record['notes']) == 0:
                        exist_note = True

                if line.addons_note:
                    if line.addons_note == record['addons_note']:
                        exist_addons_note = True
                else:
                    if len(record['addons_note']) == 0:
                        exist_addons_note = True

                if line.removable_ingredients_note:
                    if line.removable_ingredients_note == record['removable_ingredients_note']:
                        exist_remove_note = True
                else:
                    if len(record['removable_ingredients_note']) == 0:
                        exist_remove_note = True

                if line.product_id.id == product.id and exist_note and exist_addons_note and exist_remove_note:
                    line.product_uom_qty = line.product_uom_qty + record['quantity']
                    line.notes = record['notes']
                    line.name = product.name
                    line.addons_note = record['addons_note']
                    line.price_unit = record['price']
                    line.removable_ingredients_note = record['removable_ingredients_note']
                    line.combo_content = record['combo_content']
                    exist = True
                    quotation_line = request.env['sale.order.line'].sudo().search([('id', '=', line.id)])

                    quotation_line.with_context(lang='ar_001').update(
                        {'kitchen_notes': kitchen_notes_ar})

                    quotation_line.update({'kitchen_notes': kitchen_notes_en})
                    break

            if not exist:
                quotation_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    "price_unit": record['price'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    "combo_content": record['combo_content'],
                    # "price_unit": self.get_promo_price(product.id)
                })

                quotation_line.with_context(lang='ar_001').update(
                    {'kitchen_notes': kitchen_notes_ar})

                quotation_line.update({'kitchen_notes': kitchen_notes_en})

            # else:

            # exist = False
            #
            # quotation_line = request.env['sale.order.line'].sudo().create({
            #     "order_id": quotation.id,
            #     "product_id": product.id,
            #     "product_uom_qty": record['quantity'],
            #     "notes": record['notes'],
            #     'name': product.name,
            #     "price_unit": record['price'],
            #     "addons_note": record['addons_note'],
            #     "removable_ingredients_note": record['removable_ingredients_note'],
            #     "combo_content": record['combo_content'],
            #     # "price_unit": self.get_promo_price(product.id)
            # })
            # quotation_line.with_context(lang='ar_001').update(
            #     {'kitchen_notes': kitchen_notes_ar})
            # quotation_line.update({'kitchen_notes': kitchen_notes_en})

        # if lang == 'ar':
        #     kitchen_notes = kitchen_notes_ar
        # else:
        #     kitchen_notes = kitchen_notes_en
        # quotation_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation.id)])
        # for quotation_line in quotation_lines:
        #     order_line_value = {
        #         'order_line_id': quotation_line.id,
        #         'product_id': quotation_line.product_id.id,
        #         'product_tmpl_id': quotation_line.product_id.product_tmpl_id.id,
        #         "name": Product_Info.get_the_full_product_product_name(quotation_line.product_id.id,lang),
        #         'quantity': quotation_line.product_uom_qty,
        #         'price_unit': quotation_line.price_unit,
        #         "kitchen_notes":kitchen_notes,
        #         'notes': quotation_line.notes,
        #         'addons_note': quotation_line.addons_note if quotation_line.addons_note else [],
        #         'removable_ingredients_note': quotation_line.removable_ingredients_note  if quotation_line.removable_ingredients_note else [],
        #         'combo_content': quotation_line.combo_content  if quotation_line.combo_content else [],
        #         "product_main_image": "/web/content/" + str(
        #             quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",
        #         "product_main_image_path": base_url + "/web/content/" + str(
        #             quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",
        #
        #     }
        #     order_line.append(order_line_value)

        order_line = self.get_items_cart(quotation.id, lang)
        Response.status = '200'

        response = {'status': 200, 'order_lines': order_line, 'message': 'product added to cart'}
        return response

    def get_items_cart(self, quotation_id, lang):
        Product_Info = ProductInfo()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        order_line_list = []
        quotation_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation_id)])

        for quotation_line in quotation_lines:

            old_price = quotation_line.price_unit
            removables = []
            addons = []
            if quotation_line.addons_note:
                addons = quotation_line.addons_note
                for addon in addons:
                    product_add_on = request.env['product.product'].sudo().search([('id', '=', addon['product_id'])])
                    if len(product_add_on) > 0:
                        addon['price'] = Product_Info.get_product_product_price(product_add_on)
                    else:
                        addons.remove(addon)

            if quotation_line.removable_ingredients_note:
                removables = quotation_line.removable_ingredients_note
                for remove_item in removables:
                    product_removable = request.env['product.product'].sudo().search(
                        [('id', '=', remove_item['product_id'])])
                    if len(product_removable) == 0:
                        removables.remove(product_removable)

            ordreline = request.env['sale.order.line'].sudo().search([('id', '=', quotation_line.id)])
            ordreline.update(
                {
                    'addons_note': addons,
                    'removable_ingredients_note': removables,
                }
            )

            kitchen_notes_ar = Product_Info.create_kitchen_notes_new(
                quotation_line.notes, addons, removables,
                quotation_line.combo_content, "ar",ordreline.product_id)
            kitchen_notes_en = Product_Info.create_kitchen_notes_new(
                quotation_line.notes, addons, removables,
                quotation_line.combo_content, "en",ordreline.product_id)

            ordreline.with_context(lang='ar_001').update(
                {'kitchen_notes': kitchen_notes_ar})

            ordreline.update({'kitchen_notes': kitchen_notes_en})

            if lang == 'ar':
                kitchen_notes = kitchen_notes_ar
            else:
                kitchen_notes = kitchen_notes_en

            get_price_line_value = self.get_price_line(quotation_line.product_id, addons)

            ordreline.update({'price_unit': get_price_line_value['price']})

            if quotation_line.addons_note:
                if len(quotation_line.addons_note) > 0:
                    new_add_on_list = self.add_name_to_list(quotation_line.addons_note, lang)
                else:
                    new_add_on_list = []
            else:
                new_add_on_list = []

            if quotation_line.removable_ingredients_note:
                if len(quotation_line.removable_ingredients_note) > 0:
                    new_remove_list = self.add_name_to_list(quotation_line.removable_ingredients_note, lang)
                else:
                    new_remove_list = []
            else:
                new_remove_list = []

            if quotation_line.combo_content:
                if len(quotation_line.combo_content) > 0:
                    new_combo_content_list = self.add_name_to_list(quotation_line.combo_content, lang)
                else:
                    new_combo_content_list = []
            else:
                new_combo_content_list = []

            order_line_value = {
                'order_line_id': quotation_line.id,
                'product_id': quotation_line.product_id.id,
                'product_tmpl_id': quotation_line.product_id.product_tmpl_id.id,
                "name": Product_Info.get_the_full_product_product_name(quotation_line.product_id.id, lang),
                'quantity': quotation_line.product_uom_qty,
                'price_unit': get_price_line_value['price'],
                "kitchen_notes": kitchen_notes,
                'notes': quotation_line.notes,
                'addons_note': new_add_on_list,
                'removable_ingredients_note': new_remove_list,
                'combo_content': new_combo_content_list,
                "product_main_image": "/web/content/" + str(
                    quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",
                "product_main_image_path": base_url + "/web/content/" + str(
                    quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",
                "old_price": old_price

            }
            order_line_list.append(order_line_value)
        return order_line_list

    def add_name_to_list(self, list_of_items, lang):
        Product_Info = ProductInfo()
        for item in list_of_items:
            item['name'] = Product_Info.get_the_full_product_product_name(item['product_id'], lang)

        return list_of_items

    def get_price_line(self, product, addons):

        Product_Info = ProductInfo()

        return_value = {}
        if product.app_publish == True:

            addon_price = 0
            if addons:
                addon_price = 0
                for addon in addons:

                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])
                    if len(product_addon) != 0:
                        try:
                            res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = product_addon.lst_price

                        price_without_TVA = Product_Info.get_product_product_price(product_addon)

                        addon_price = addon_price + price_without_TVA

            price_product_without_tva = round(Product_Info.get_product_product_price(product) + addon_price, 3)

            return_value = {
                "product_found": True,
                "price": price_product_without_tva
            }
        else:
            return_value = {
                "product_found": False,
                "price": 0.0
            }
        return return_value

    @http.route(ProductInfo.version + 'update-cart-item', type='json', auth='public', methods=['Post'], cors="*")
    def update_cart_item(self):
        Product_Info = ProductInfo()
        order_line_list = []
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        order_line_id = req.get('order_line_id')

        order_line = request.env['sale.order.line'].sudo().search([('id', '=', order_line_id)])
        if not order_line:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response

        quotation = order_line.order_id
        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response
        # partner_id', '=', retailer_user.partner_id.id

        if quotation.user_place_order:
            Response.status = '404'
            response = {'status': 404, 'message': 'Quotation can not be updated'}
            return response

        if quotation.partner_id != retailer_user.partner_id:
            Response.status = '404'
            response = {'status': 404, 'message': 'Different user'}
            return response

        if not req.get('products'):
            Response.status = '404'
            response = {'status': 404, 'message': 'Products is required'}
            return response
        # try:
        if not isinstance(req.get('products'), list):
            Response.status = '404'
            response = {'status': 404, 'message': 'Products must be list'}
            return response
        if len(req.get('products')) == 0:
            Response.status = '404'
            response = {'status': 404, 'message': 'Products is required'}
            return response

        for record in req.get('products'):

            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])
            if len(product) == 0:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found', 'product_id': record['product_id']}
                return response
            # the_check_response = self.check_prices(product, record['addons_note'], record['price'])
            # if the_check_response['status'] != 200:
            #     Response.status = the_check_response['status']
            #     response = the_check_response
            #     return response
            #######################
            if product.app_publish == True:

                addon_price = 0
                addons = record['addons_note']
                if addons:
                    addon_price = 0
                    for addon in addons:

                        product_addon = request.env['product.product'].sudo().search(
                            [('id', '=', addon['product_id'])])
                        if len(product_addon) == 0:
                            Response.status = '404'
                            response = {'status': 404, 'message': 'Add On Not Found', 'add_on_id': addon['product_id']}
                            return response

                        try:
                            res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = product_addon.lst_price

                        price_without_TVA = Product_Info.get_product_product_price(product_addon)
                        if addon['price'] != price_without_TVA:
                            Response.status = '404'
                            values = Product_Info.get_product_product_details(product_addon)
                            response = {'status': 404, 'message': 'Add On Price Not Correct',
                                        'product_id': addon['product_id'], 'product_name': product_addon.name,
                                        'final_price_Without_TVA': values['final_price_Without_TVA'],
                                        'final_price': values['final_price']}
                            return response
                        addon_price = addon_price + addon['price']

                # price_unit = record['price']

                try:
                    res = product.taxes_id.compute_all(product.lst_price, product=product)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = product.lst_price

                price_product_without_tva = round(Product_Info.get_product_product_price(product), 3)

                if round((record['price'] - addon_price), 3) != price_product_without_tva:
                    Response.status = '404'
                    values = Product_Info.get_product_product_details(product)
                    response = {'status': 404, 'message': 'Price Not Correct',
                                'product_id': product.id, 'product_name': product.name,
                                'final_price_Without_TVA': values['final_price_Without_TVA'],
                                'final_price': values['final_price']}
                    return response
                # Response.status = '200'
                # response = {'status': 200}
                # return response
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Available', 'product_id': product.id,
                            'product_name': product.name}
                return response
            ########################
            if order_line:
                order_line.product_id = product
                order_line.product_uom_qty = record['quantity']
                order_line.notes = record['notes']
                order_line.name = product.name
                order_line.addons_note = record['addons_note']
                order_line.price_unit = record['price']
                order_line.removable_ingredients_note = record['removable_ingredients_note']
                order_line.combo_content = record['combo_content']

                quotation_line = request.env['sale.order.line'].sudo().search([('id', '=', order_line.id)])
                quotation_line.with_context(lang='ar_001').update(
                    {'kitchen_notes': Product_Info.create_kitchen_notes_new(
                        record['notes'], record['addons_note'], record['removable_ingredients_note'],
                        record['combo_content'], "ar",quotation_line.product_id)})
                quotation_line.update({'kitchen_notes': Product_Info.create_kitchen_notes_new(record['notes'], record[ 'addons_note'],
                                                                                              record[ 'removable_ingredients_note'],
                                                                                              record[ 'combo_content'], "en",quotation_line.product_id)})

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        order_line_list = self.get_items_cart(quotation.id, lang)

        Response.status = '200'
        response = {'status': 200, 'order_lines': order_line_list, 'message': 'order line updated'}
        return response

    @http.route(ProductInfo.version + 'cart-items-count', type='json', auth='public', methods=['Post'], cors="*")
    def cart_items_count(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        company_id = req.get('company_id')
        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('company_id', '=', company_id), ('state', '=', 'draft'),
             ('sale_order_type', 'in', ['1', '2']),('user_place_order', '=', False)])



        if not quotation:
            Response.status = '200'
            response = {'status': 200,'order_lines_count': 0, 'message': 'user does not have cart'}
            return response

        order_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation.id)])
        if order_lines:
            order_lines_count = len(order_lines)
        else:
            order_lines_count = 0
        Response.status = '200'
        response = {'status': 200, 'order_lines_count': order_lines_count, 'message': 'order lines count'}
        return response

    @http.route(ProductInfo.version + 'cart-items', type='json', auth='public', methods=['Post'], cors="*")
    def cart_items(self):


        order_line_list = []
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        company_id = req.get('company_id')

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('company_id', '=', company_id), ('state', '=', 'draft'),
             ('sale_order_type', 'in', ['1', '2']),('user_place_order', '=', False)])



        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'user does not have cart'}
            return response

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        order_line_list = []
        order_line_list = self.get_items_cart(quotation.id, lang)
        Response.status = '200'
        response = {'status': 200, 'order_lines': order_line_list, 'message': 'order line list'}
        return response

    @http.route(ProductInfo.version + 'cart-items-next', type='json', auth='public', methods=['Post'], cors="*")
    def cart_items_next(self):

        order_line_list = []
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        company_id = req.get('company_id')

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('company_id', '=', company_id), ('state', '=', 'draft'),
             ('sale_order_type', 'in', ['1', '2']), ('user_place_order', '=', False)])

        if not quotation:
            Response.status = '200'
            response = {'status': 200, 'order_lines': [],'message': 'user does not have cart'}
            return response

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        order_line_list = []
        order_line_list = self.get_items_cart(quotation.id, lang)

        Response.status = '200'
        response = {'status': 200, 'order_lines': order_line_list, 'message': 'order line list'}
        return response

    @http.route(ProductInfo.version + 'empty-cart', type='json', auth='public', methods=['Post'], cors="*")
    def empty_cart(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        company_id = req.get('company_id')
        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('company_id', '=', company_id), ('state', '=', 'draft'),
             ('sale_order_type', 'in', ['1', '2']),('user_place_order', '=', False)])

        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'user does not have cart'}
            return response
        if quotation.user_place_order:
            Response.status = '404'
            response = {'status': 404, 'message': 'Quotation can not be munpulated'}
            return response
        quotation_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation.id)])
        try:
            for quotation_line in quotation_lines:
                quotation_line.sudo().unlink()
            Response.status = '200'
            response = {'status': 200, 'message': 'Empty Cart'}
        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}

        return response

    @http.route(ProductInfo.version + 'remove-cart-item', type='json', auth='public', methods=['Post'], cors="*")
    def remove_cart_item(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        order_line_id = req.get('order_line_id')

        order_line = request.env['sale.order.line'].sudo().search([('id', '=', order_line_id)])
        if not order_line:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response

        quotation = order_line.order_id
        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response
        # partner_id', '=', retailer_user.partner_id.id
        if quotation.partner_id != retailer_user.partner_id:
            Response.status = '404'
            response = {'status': 404, 'message': 'Different user'}
            return response

        try:
            order_line.sudo().unlink()
            Response.status = '200'
            response = {'status': 200, 'message': 'Remove Cart Item Done!'}
        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}

        return response

    @http.route(ProductInfo.version + 'update-cart-item-quantity', type='json', auth='public', methods=['Post'],
                cors="*")
    def update_cart_item_quantity(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        order_line_id = req.get('order_line_id')
        increase_or_decrease = req.get('increase_or_decrease')
        order_line = request.env['sale.order.line'].sudo().search([('id', '=', order_line_id)])
        if not order_line:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response

        quotation = order_line.order_id
        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'Wrong quotation'}
            return response

        if quotation.user_place_order:
            Response.status = '404'
            response = {'status': 404, 'message': 'Quotation can not be updated'}
            return response

        # partner_id', '=', retailer_user.partner_id.id
        if quotation.partner_id != retailer_user.partner_id:
            Response.status = '404'
            response = {'status': 404, 'message': 'Different user'}
            return response

        try:
            qtity = order_line.product_uom_qty
            if increase_or_decrease:
                qtity = qtity + 1
            else:
                qtity = qtity - 1
            if qtity <= 0:
                Response.status = '403'
                response = {'status': 403, 'message': 'not allowed!'}
                return response
            order_line.sudo().update({
                'product_uom_qty': qtity
            })
            Response.status = '200'
            response = {'status': 200, 'message': 'update-cart-item-quantity Done!'}
        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}

        return response