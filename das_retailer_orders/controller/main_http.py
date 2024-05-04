from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
import logging
from odoo.addons.das_publicfunction.controller.main import ProductInfo

_logger = logging.getLogger(__name__)


class ProductRetailerOrder(http.Controller):

    @http.route(ProductInfo.version + 'wishlist-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_wishlist(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            company_id = int(request.params.get('company_id'))
            test_company = True
        except:
            company_id = -1
            test_company = False

        try:
            user_id = int(request.params.get('user_id'))

        except:
            user_id = -1


        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if retailer_user:
                all_wishlist = request.env['product.wishlist'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id)])
                wish_list = []
                Product_Info = ProductInfo()
                if all_wishlist:
                    for wish in all_wishlist:
                        if test_company:
                            if wish.product_template_id.company_id:
                                if wish.product_template_id.company_id.id != company_id:
                                    continue

                        try:
                            res = wish.product_template_id.taxes_id.compute_all(wish.product_template_id.list_price,
                                                                                product=wish.product_template_id)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = wish.product_template_id.list_price
                        product_template_price_json = Product_Info.get_product_template_price_json(
                            wish.product_template_id)

                        try:
                            new_price = product_template_price_json['new_price']
                            new_price = round(new_price, 2)
                        except:
                            new_price = product_template_price_json['new_price']

                        try:
                            percent_discount = product_template_price_json['percent_discount']
                            percent_discount = round(percent_discount, 2)
                        except:
                            percent_discount = product_template_price_json['percent_discount']

                        if company_id == -1:
                            thecompany_id = company_id
                        values = {
                            "product_id": wish.product_template_id.id,
                            "product_name": wish.product_template_id.name,
                            "product_image": base_url + "/web/content/" + str(wish.product_template_id.image_attachment.id) if wish.product_template_id.image_attachment.id else "",
                            # "price": wish.product_template_id.list_price,
                            "price": Product_Info.get_product_template_price(wish.product_template_id),
                            'template_sale_price_new': new_price,
                            'template_sale_price_old': round(price_product, 2),
                            'percent_discount': percent_discount,
                            "is_fav": True,
                            "variant_discount": Product_Info.has_variant_discount(wish.product_template_id.id, thecompany_id)
                        }
                        wish_list.append(values)
                    Response.status = '200'
                    response = {'status': 200, 'response': wish_list, 'message': 'Wishlist Found'}
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'No Wishlist Found!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'all-products-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_list_of_products(self):
        x_localization = request.httprequest.headers.get('x-localization')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        lang = "en"

        try:
            company_id = int(request.params.get('company_id'))
            test_company = True
        except:
            company_id = -1
            test_company = False
        if company_id == None:
            company_id = -1
            test_company = False

        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            if test_company:
                products = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service'),('company_id', 'in', [company_id,False])])
            else:
                products = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service')])
        else:
            if test_company:
                products = request.env['product.template'].sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service'), ('company_id', 'in', [company_id, False])])
            else:
                products = request.env['product.template'].sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service')])

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = False
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False


        list = []
        Product_Info = ProductInfo()
        if products:
            for product in products:
                if product.company_id:
                    thecompany_id = product.company_id.id
                else:
                    thecompany_id = False

                is_fav = False
                if retailer_user:
                    all_wishlist = request.env['product.wishlist'].sudo().search(
                        [('partner_id', '=', retailer_user.partner_id.id),
                         ('product_id.product_tmpl_id', '=', product.id)])
                else:
                    all_wishlist = False

                if all_wishlist:
                    is_fav = True

                try:
                    res = product.taxes_id.compute_all(product.list_price, product=product)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = product.list_price

                product_template_price_json = Product_Info.get_product_template_price_json(product)
                try:
                    new_price = product_template_price_json['new_price']
                    new_price = round(new_price, 2)
                except:
                    new_price = product_template_price_json['new_price']

                try:
                    percent_discount = product_template_price_json['percent_discount']
                    percent_discount = round(percent_discount, 2)
                except:
                    percent_discount = product_template_price_json['percent_discount']

                the_price = Product_Info.get_product_template_price(product)
                
                values = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": base_url + "/web/content/" + str(
                        product.image_attachment.id) if product.image_attachment.id else "",
                    "price": the_price,
                    "price_list": Product_Info.get_prices_for_currency_list(the_price,thecompany_id),
                    'template_sale_price_new': new_price,
                    'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                        new_price, company_id),
                    'template_sale_price_old': round(price_product, 2),
                    'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                        price_product, company_id),
                    'percent_discount': percent_discount,
                    "category_id":product.categ_id.id,
                    "is_fav": is_fav,
                    "variant_discount": Product_Info.has_variant_discount(product.id, thecompany_id)
                }
                list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status = '200'
            response = {'status': 200, 'response': [],'message': 'no products found'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])


    @http.route(ProductInfo.version + 'product-information-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_product_information_by_id(self):

        x_localization = request.httprequest.headers.get('x-localization')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        lang = "en"

        try:
            product_tmpl_id = int(request.params.get('product_tmpl_id'))
        except:
            product_tmpl_id = False

        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            product_id = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                [('id', '=', product_tmpl_id)])

        else:
            product_id = request.env['product.template'].sudo().search([('id', '=', product_tmpl_id)])

        # boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

        if product_id.company_id:
            company_id = product_id.company_id.id
        else:
            company_id = False
        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = False

        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        # if retailer_user:
        #     all_wishlist = request.env['product.wishlist'].sudo().search(
        #         [('partner_id', '=', retailer_user.partner_id.id)])
        # else:
        #     all_wishlist = False

        if retailer_user:
            all_wishlist = request.env['product.wishlist'].sudo().search(
                [('partner_id', '=', retailer_user.partner_id.id), ('product_id.product_tmpl_id', '=', product_id.id)])
        else:
            all_wishlist = False

        if product_id:

            images = request.env['product.image'].sudo().search(
                [('product_tmpl_id', '=', product_id.id)])
            images_list = []
            if product_id.image_attachment:
                images_list.append(base_url + "/web/content/" + str(product_id.image_attachment.id))
            for image in images:
                images_list.append(base_url + "/web/content/" + str(image.image_attachment.id))
            is_fav = False

            details = ProductInfo()
            if all_wishlist:
                is_fav = True
                # for wish in all_wishlist:
                #     if product_id.id == wish.product_id.product_tmpl_id.id:
                #         is_fav = True
                #         break

            try:
                res = product_id.taxes_id.compute_all(product_id.list_price, product=product_id)
                included = res['total_included']
                price_product = included
            except:
                price_product = product_id.list_price

            template_sale_price_new = details.get_product_template_price(product_id)

            drinks_caption = ''
            sides_caption = ''
            related_caption = ''
            liked_caption = ''
            desserts_caption = ''
            try:
                if lang == "ar":
                    captions = request.env['das.caption'].with_context(lang='ar_001').sudo().search([])
                else:
                    captions = request.env['das.caption'].sudo().search([])


                if captions:
                    drinks_caption = captions.drinks_caption
                    sides_caption = captions.sides_caption
                    related_caption = captions.related_caption
                    liked_caption = captions.liked_caption
                    desserts_caption = captions.desserts_caption

            except:
                pass

            values = {
                "product_tmpl_id": product_id.id,
                "product_name": product_id.name,
                "product_description": details.change_parag_to_line(product_id.description_sale),
                "product_main_image": base_url + "/web/content/" + str(
                    product_id.image_attachment.id) if product_id.image_attachment.id else "",
                "product_images": images_list,
                'is_fav': is_fav,
                'is_combo': product_id.is_combo,
                'template_sale_price_old': round(price_product,2),
                'template_sale_price_old_list': details.get_prices_for_currency_list(price_product,company_id),
                'template_sale_price_new': template_sale_price_new,
                'template_sale_price_new_list': details.get_prices_for_currency_list(template_sale_price_new,company_id),
                'product_template_details': details.get_product_template_details(product_id, lang),
                'Addons_details': details.get_add_ons(product_id,lang),
                'Ingredients_details': details.get_ingredients(product_id,lang),
                'Removable_Ingredients_details': details.get_removale_ingredients(product_id,lang),

                # 'Drinks_mendatory': product_id.drinks_mendatory,
                'Drinks_caption': drinks_caption,
                'Drinks_details': details.get_drinks_product(product_id,lang),
                # 'Drink_default':  product_id.default_drink_id.id if product_id.default_drink_id.id else -1,

                # 'Sides_mendatory': product_id.sides_mendatory,
                'Sides_caption': sides_caption,
                'Sides_Products_details': details.get_sides_product(product_id,lang),
                # 'Side_default': product_id.default_sides_id.id if product_id.default_sides_id.id else -1,

                'Related_caption': related_caption,
                'Related_Products_details': details.get_related_product(product_id,lang),

                'Also_Like_caption': liked_caption,
                'Also_Like_Products_details': details.get_also_like_product(product_id,lang),

                'Desserts_caption': desserts_caption,
                'Desserts_Products_details': details.get_desserts_product(product_id,lang),

                'Product_attributes': details.get_attribute_product_new(product_id, lang),

                'Product_contents': details.get_product_contents(product_id, lang)

            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Product Information'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'list-user-addresses-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_list_of_other_address(self):

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        detail = ProductInfo()
        list = []
        if retailer_user:
            if retailer_user.partner_id:

                lat = 0
                long = 0
                if retailer_user.partner_id.child_ids:
                    try:
                        free_delivery = retailer_user.partner_id.free_delivery
                    except:
                        free_delivery = False

                    for add in retailer_user.partner_id.child_ids:
                        lat = add.partner_latitude if add.partner_latitude else 0
                        long = add.partner_longitude if add.partner_longitude else 0
                        values = {
                            "address_id": add.id,
                            "address_name": add.name,
                            "mobile": add.mobile if add.mobile else "",
                            "phone": add.phone if add.phone else "",
                            # "street_id": add.street_id.id if add.street_id.id else 0,
                            "street_name": add.street if add.street else "",
                            # "city_id": add.city_id.id if add.city_id.id else 0,
                            "city_name": add.city if add.city else "",
                            "state_id": add.state_id.id if add.state_id.id else 0,
                            "state_name": add.state_id.name if add.state_id.name else "",
                            "near": add.street2 if add.street2 else "",
                            "lat": lat,
                            "long": long,
                            "zone_id": add.zone_id.id if add.zone_id else None,
                            "can_delete": True,
                            "delivery_info": detail.calcul_for_address(lat, long, None, free_delivery)
                        }
                        list.append(values)

                Response.status = '200'
                response = {'status': 200, 'response': list, 'message': 'list other address'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'no other address found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'orders-history-http', type='http', auth='public', methods=['Get'], cors='*')
    def get_history_orders(self):
        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        retailer_user = request.env['res.users'].sudo().search([('id', '=',user_id)])
        if retailer_user:
            # sale_orders_delivered = quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],order='create_date Desc')

            # quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],
            #     order='create_date Desc')

            if lang == "ar":
                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search([('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],order='create_date Desc')
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],
                    order='create_date Desc')

            orders = []
            if lang == "ar":
                order_status = "تم التوصيل"
            else:
                order_status = "Delivered"
            delivery_product = request.env['product.product'].sudo().search(
                [('is_delivery', '=', True)], limit=1)

            if quotations:
                for order in quotations:
                    delivery_charge = 0
                    products = []
                    for line in order.order_line:
                        if order.sale_order_type == "1":

                            if delivery_product.id == line.product_id.id:
                                delivery_charge = line.price_total
                        else:
                            delivery_charge = 0
                        try:
                            the_notes = line.kitchen_notes
                        except:
                            the_notes = line.notes
                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": the_notes if the_notes else "",
                                "product_image": base_url + "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total / int(line.product_uom_qty), 2)
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
                            "amount": order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": "7",
                            "products": products
                        }
                    )
                Response.status  = '200'
                response = {'status': 200, 'response': orders, 'message': 'list of orders found'}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'no orders found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User not found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'current-orders-http', type='http', auth='public', methods=['Get'], cors='*')
    def get_current_orders(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if retailer_user:
            # quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '!=', '7'),
            #      ('state', '!=', 'cancel')],
            #     order='create_date Desc')
            if lang == "ar":
                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search([('partner_id', '=', retailer_user.partner_id.id), ('order_status', '!=', '7'),('sale_order_type', '!=', '3'),('state', '!=', 'cancel')],order='create_date Desc')
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '!=', '7'),('sale_order_type', '!=', '3'),('state', '!=', 'cancel')],
                    order='create_date Desc')

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
                    # if order.order_status == "2":
                    #     order_status = "Draft"
                    # elif order.order_status == "3":
                    #     order_status = "Confirmed"
                    # elif order.order_status == "4":
                    #     order_status = "In Progress"
                    # elif order.order_status == "5":
                    #     order_status = "Ready"
                    # elif order.order_status == "6":
                    #     order_status = "Out For Delivery"
                    # elif order.order_status == "7":
                    #     order_status = "Delivered"

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
                            # order_status = "In Progress"
                            if lang == "ar":
                                order_status = "قيد التحضير"
                            else:
                                order_status = "In Progress"

                    products = []
                    delivery_charge = 0

                    for line in order.order_line:
                        if order.sale_order_type == "1":

                            if delivery_product.id == line.product_id.id:
                                delivery_charge = line.price_total
                        else:
                            delivery_charge = 0
                        try:
                            the_notes = line.kitchen_notes
                        except:
                            the_notes = line.notes
                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": line.notes if line.notes else "",
                                "product_image": base_url + "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total / int(line.product_uom_qty), 2)
                            }
                            products.append(values)

                    try:
                        order_date = order.date_order.date()
                        order_datetime = order_date.strftime('%Y-%m-%d')
                    except:
                        order_datetime = ""

                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id": order.sale_order_type,
                            "delivery_fees": delivery_charge,
                            "order_date": order_datetime,
                            "amount": order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": order_status_id,
                            "products": products
                        }
                    )
                Response.status  = '200'
                response = {'status': 200, 'response': orders, 'message': 'list of orders found'}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'no orders found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User not found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'products-name-translate-http', type='http', auth='public', methods=['Get'], cors="*")
    def products_name_translate_http(self):
        Product_Info = ProductInfo()

        products_result_list = []
        products_list1 = []
        # products_list = request.params.get('products')
        products_string = request.params.get('products')

        # Parse the string into a list
        products_list = json.loads(products_string)



        company_id =  request.params.get('company_id')

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if products_list:
            for product in products_list:
                product_id = product['product_id']

                if lang == 'ar':
                    product_product = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                        [('id', '=', product_id)])
                else:
                    product_product = request.env['product.product'].sudo().search(
                        [('id', '=', product_id)])

                thename = product_product.name

                variant_name = Product_Info.get_product_variant_name(product_product)

                if variant_name != '':
                    variant_name = ' (' + variant_name + ')'
                if variant_name:
                    thename = thename + variant_name
                val = {
                    "product_id": product_id,
                    "name": thename if thename else ""
                }
                addons_note_list = []
                if "addons_note" in product:

                    for addon_id in product['addons_note']:
                        if lang == 'ar':

                            addon_addon = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                                [('id', '=', addon_id)])
                        else:
                            addon_addon = request.env['product.product'].sudo().search(
                                [('id', '=', addon_id)])
                        thename = addon_addon.name
                        variant_name = Product_Info.get_product_variant_name(addon_addon)
                        if variant_name != '':
                            variant_name = ' (' + variant_name + ')'
                        if variant_name:
                            thename = thename + variant_name
                        value_add_on = {
                            "product_id": addon_id,
                            "name": thename if thename else ""
                        }
                        addons_note_list.append(value_add_on)
                val['addons_note'] = addons_note_list

                removable_ingredients_note_list = []
                if "removable_ingredients_note" in product:

                    for removable_ingredient_id in product['removable_ingredients_note']:
                        if lang == 'ar':

                            removable_ingredient = request.env['product.product'].with_context(
                                lang='ar_001').sudo().search(
                                [('id', '=', removable_ingredient_id)])
                        else:
                            removable_ingredient = request.env['product.product'].sudo().search(
                                [('id', '=', removable_ingredient_id)])
                        thename = removable_ingredient.name
                        variant_name = Product_Info.get_product_variant_name(removable_ingredient)
                        if variant_name != '':
                            variant_name = ' (' + variant_name + ')'
                        if variant_name:
                            thename = thename + variant_name
                        value_removable_ingredient = {
                            "product_id": removable_ingredient_id,
                            "name": thename if thename else ""
                        }
                        removable_ingredients_note_list.append(value_removable_ingredient)
                val['removable_ingredients_note'] = removable_ingredients_note_list
                products_result_list.append(val)

            Response.status = '200'
            response = {'status': 200, 'response': products_result_list, 'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'list of products not found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route(ProductInfo.version + 'current-order-details-http', type='http', auth='public', methods=['Get'], cors='*')
    def get_current_order_details_http(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1
        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        try:
            order_id = int(request.params.get('order_id'))
        except:
            order_id = -1
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
                        try:
                            the_notes = line.kitchen_notes
                        except:
                            the_notes = line.notes
                        if delivery_product.id != line.product_id.id:
                            values = {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.product_tmpl_id.name,
                                "notes": the_notes if the_notes else "",
                                "product_image": base_url + "/web/content/" + str(
                                    line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total / int(line.product_uom_qty), 2)
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
                            "amount": order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id": order_status_id,
                            "products": products
                        }
                    )
                Response.status = '200'
                response = {'status': 200, 'response': orders[0], 'message': 'Details of order found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'no order found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User not found'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
