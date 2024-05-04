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
from  odoo.addons.das_publicfunction.controller.main import ProductInfo

from  odoo.addons.das_first_order.controller.main import FirstOrderDiscount

from odoo.addons.web.models.ir_http import Http
from odoo.addons.das_user_notification.controller.main import Notification
from collections import defaultdict
_logger = logging.getLogger(__name__)


class ProductRetailerOrder(http.Controller):



    def get_available_quantity(self, product_id, warehouse_id):
        lines = request.env['stock.quant'].sudo().search(
            [('product_id', '=', product_id)])
        sum_quantity = 0
        for line in lines:
            if line.location_id.warehouse_id.id == warehouse_id and line.location_id.usage == 'internal':
                sum_quantity += line.available_quantity
        return int(sum_quantity)



    # wishlist list
    @http.route(ProductInfo.version + 'wishlist', type='json', auth='public', methods=['Post'], cors="*")
    def get_wishlist(self):
        req = json.loads(request.httprequest.data)
        try:
            company_id = req.get('company_id')
            test_company = True
        except:
            company_id = -1
            test_company = False
        user_id = req.get('user_id')

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if retailer_user:
                all_wishlist = request.env['product.wishlist'].sudo().search([('partner_id', '=', retailer_user.partner_id.id)])
                wish_list = []
                Product_Info = ProductInfo()
                if all_wishlist:
                    for wish in all_wishlist:
                        if test_company:
                            if wish.product_template_id.company_id:
                                if wish.product_template_id.company_id.id !=company_id :
                                    continue

                        try:
                            res = wish.product_template_id.taxes_id.compute_all(wish.product_template_id.list_price, product=wish.product_template_id)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = wish.product_template_id.list_price
                        product_template_price_json = Product_Info.get_product_template_price_json(wish.product_template_id)


                        try:
                            new_price = product_template_price_json['new_price']
                            new_price = round(new_price,2)
                        except:
                            new_price = product_template_price_json['new_price']

                        try:
                            percent_discount = product_template_price_json['percent_discount']
                            percent_discount = round(percent_discount,2)
                        except:
                            percent_discount = product_template_price_json['percent_discount']

                        if company_id == -1:
                            thecompany_id = company_id
                        else:
                            thecompany_id = False
                        values = {
                            "product_id": wish.product_template_id.id,
                            "product_name": wish.product_template_id.name,
                            "product_image": "/web/content/" + str(wish.product_template_id.image_attachment.id) if wish.product_template_id.image_attachment.id else "",
                            "product_image_path": base_url + "/web/content/" + str(wish.product_template_id.image_attachment.id) if wish.product_template_id.image_attachment.id else "",
                            "price": Product_Info.get_product_template_price(wish.product_template_id),
                            'template_sale_price_new': round(new_price,2),
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
        return response

    @http.route(ProductInfo.version + 'wishlist-next', type='json', auth='public', methods=['Post'], cors="*")
    def get_wishlist_next(self):
        req = json.loads(request.httprequest.data)
        try:
            company_id = req.get('company_id')
            test_company = True
        except:
            company_id = -1
            test_company = False
        user_id = req.get('user_id')

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

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
                        else:
                            thecompany_id = False
                        values = {
                            "product_id": wish.product_template_id.id,
                            "product_name": wish.product_template_id.name,
                            "product_image": "/web/content/" + str(
                                wish.product_template_id.image_attachment.id) if wish.product_template_id.image_attachment.id else "",
                            "product_image_path": base_url + "/web/content/" + str(
                                wish.product_template_id.image_attachment.id) if wish.product_template_id.image_attachment.id else "",
                            "price": Product_Info.get_product_template_price(wish.product_template_id),
                            'template_sale_price_new': round(new_price, 2),
                            'template_sale_price_old': round(price_product, 2),
                            'percent_discount': percent_discount,
                            "is_fav": True,
                            "variant_discount": Product_Info.has_variant_discount(wish.product_template_id.id,
                                                                                  thecompany_id)
                        }
                        wish_list.append(values)
                    Response.status = '200'
                    response = {'status': 200, 'response': wish_list, 'message': 'Wishlist Found'}
                else:
                    Response.status = '200'
                    response = {'status': 200, 'response': [],'message': 'No Wishlist Found!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'response': [], 'message': 'User Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'response': [], 'message': 'User Not Found!'}
        return response

    #     add to wishlist
    @http.route(ProductInfo.version + 'add-to-wishlist', type='json', auth='public', methods=['Post'], cors="*")
    def add_to_wishlist(self):
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if retailer_user:
                product_id = request.env['product.template'].sudo().search([('id', '=', req.get('product_id'))])

                exist = request.env['product.wishlist'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id), ('product_template_id', '=', product_id.id)])

                if exist:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Product already added to wishlist!'}
                    return response

                if product_id:
                    product_product_id = request.env['product.product'].sudo().search([('product_tmpl_id', '=', req.get('product_id'))],limit=1)

                    wishlist_created = request.env['product.wishlist'].sudo().create(
                        {"partner_id": retailer_user.partner_id.id,
                         "product_id": product_product_id.id,
                         "product_template_id": product_id.id,
                         "website_id": 1
                         }
                    )
                    if wishlist_created:
                        Response.status = '201'
                        response = {'status': 201, 'response': wishlist_created.id, 'message': 'Wishlist Created'}
                    else:
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Not Added!'}
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Product Not Found!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        return response

    # remove from wishlist
    @http.route(ProductInfo.version + 'remove-from-wishlist', type='json', auth='public', methods=['Post'], cors="*")
    def remove_from_wishlist(self):
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if retailer_user:
                product_wishlist_id = request.env['product.wishlist'].sudo().search(
                    [('product_template_id', '=', req.get('product_id')), ('partner_id', '=', retailer_user.partner_id.id)])
                if product_wishlist_id:
                    product_wishlist_id.unlink()
                    Response.status = '200'
                    response = {'status': 200, 'message': 'Product removed from wishlist!'}
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Product Not Found!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        return response

    #     product information by id
    #ProductInfo.version
    @http.route(ProductInfo.version + 'product-information', type='json', auth='public', methods=['Post'],cors="*")
    def get_product_information_by_id(self):

        x_localization = request.httprequest.headers.get('x-localization')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        lang = "en"
        req = json.loads(request.httprequest.data)
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            product_id = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                [('id', '=', req.get('product_tmpl_id'))])

        else:
            product_id = request.env['product.template'].sudo().search([('id', '=', req.get('product_tmpl_id'))])
            
        # boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)
        
        user_id = req.get('user_id')
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
                [('partner_id', '=', retailer_user.partner_id.id),('product_id.product_tmpl_id', '=', product_id.id)])
        else:
            all_wishlist = False
            
        if product_id:

            images = request.env['product.image'].sudo().search(
                [('product_tmpl_id', '=', product_id.id)])
            images_list = []
            images_list_path = []
            if product_id.image_attachment:
                images_list.append("/web/content/" + str(product_id.image_attachment.id))
                images_list_path.append(base_url + "/web/content/" + str(product_id.image_attachment.id))
            for image in images:
                images_list.append("/web/content/" + str(image.image_attachment.id))
                images_list_path.append(base_url + "/web/content/" + str(image.image_attachment.id))
            is_fav = False
            
            details = ProductInfo()
            if all_wishlist:
                is_fav = True
                # for wish in all_wishlist:
                #     if product_id.id == wish.product_id.product_tmpl_id.id:
                #         is_fav = True
                #         break

            try:
                res = product_id.taxes_id.compute_all(product_id.list_price,product=product_id)
                included = res['total_included']
                price_product = included
            except:
                price_product = product_id.list_price

            template_sale_price_new = details.get_product_template_price(product_id)
            if product_id.company_id:
                company_id = product_id.company_id.id
            else:
                company_id = False

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
                "product_main_image": "/web/content/" + str(product_id.image_attachment.id) if product_id.image_attachment.id else "",
                "product_main_image_path": base_url + "/web/content/" + str(product_id.image_attachment.id) if product_id.image_attachment.id else "",
                "product_images": images_list,
                "product_images_path": images_list_path,
                'is_fav': is_fav,
                'is_combo':product_id.is_combo,
                'template_sale_price_old': round(price_product,2),
                'template_sale_price_old_list': details.get_prices_for_currency_list(price_product,company_id) ,
                'template_sale_price_new': template_sale_price_new ,
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
                'Sides_caption':sides_caption,
                'Sides_Products_details': details.get_sides_product(product_id,lang),
                # 'Side_default': product_id.default_sides_id.id if product_id.default_sides_id.id else -1,

                'Related_caption': related_caption,
                'Related_Products_details': details.get_related_product(product_id,lang),

                'Also_Like_caption': liked_caption,
                'Also_Like_Products_details': details.get_also_like_product(product_id,lang),

                'Desserts_caption': desserts_caption,
                'Desserts_Products_details': details.get_desserts_product(product_id,lang),

                'Product_attributes': details.get_attribute_product_new(product_id,lang),

                'Product_contents': details.get_product_contents(product_id,lang)

            }


            Response.status  = '200'
            response = {'status': 200, 'response': values, 'message': 'Product Information'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'No data found!'}
        return response

    @http.route(ProductInfo.version + 'product-related-list', type='json', auth='public', methods=['Post'], cors="*")
    def get_product_related_list(self):
        req = json.loads(request.httprequest.data)
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        productinfo = ProductInfo()
        products = req.get('products')
        product_list = []
        for product_id in products:
            if lang == "ar":
                product_template = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                    [('id', '=', product_id)])
            else:
                product_template = request.env['product.template'].sudo().search([('id', '=', product_id)])
            if product_template:
                for relt in product_template.related_ids:
                    default = False
                    
                    product_exists = any(item[0]["product_id"] == relt.id for item in product_list)
                    if product_exists == False:
                        related = productinfo.get_product_full_product_sd_details(relt, default, lang)
                        product_list.append(related)

            # return products
        Response.status = '200'
        response = {'status': 200, 'response': product_list, 'message': 'Products List'}
        return response
    @http.route(ProductInfo.version + 'product-product-information', type='json', auth='public', methods=['Post'], cors="*")
    def get_product_product_information_by_id(self):

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        req = json.loads(request.httprequest.data)
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            product_id = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                [('id', '=', req.get('product_id'))])

        else:
            product_id = request.env['product.product'].sudo().search([('id', '=', req.get('product_id'))])

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
        if product_id:


            details = ProductInfo()

            values = {
                "product_id": product_id.id,
                "product_name": product_id.name,
                "product_description": details.change_parag_to_line(product_id.description_sale),
                "product_main_image": "/web/content/" + str(product_id.product_tmpl_id.image_attachment.id) if product_id.product_tmpl_id.image_attachment.id else "",

                'template_sale_price': product_id.product_tmpl_id.list_price,
                'product_product_details': details.get_product_full_product_details(product_id,lang),  #########
                'Addons_details': details.get_add_ons(product_id.product_tmpl_id,lang),
                'Ingredients_details': details.get_ingredients(product_id.product_tmpl_id,lang),
                'Removable_Ingredients_details': details.get_removale_ingredients(product_id.product_tmpl_id,lang),

                # 'Drinks_mendatory': product_id.product_tmpl_id.drinks_mendatory,
                'Drinks_caption': drinks_caption,
                'Drinks_details': details.get_drinks_product(product_id.product_tmpl_id,lang),
                # 'Drink_default': product_id.product_tmpl_id.default_drink_id.id if product_id.product_tmpl_id.default_drink_id.id else -1,

                # 'Sides_mendatory': product_id.product_tmpl_id.sides_mendatory,
                'Sides_caption': sides_caption,
                'Sides_Products_details': details.get_sides_product(product_id.product_tmpl_id,lang),
                # 'Side_default': product_id.product_tmpl_id.default_sides_id.id if product_id.product_tmpl_id.default_sides_id.id else -1,

                'Related_caption': related_caption,
                'Related_Products_details': details.get_related_product(product_id.product_tmpl_id,lang),

                'Also_Like_caption': liked_caption,
                'Also_Like_Products_details': details.get_also_like_product(product_id.product_tmpl_id,lang),

                'Desserts_caption': desserts_caption,
                'Desserts_Products_details': details.get_desserts_product(product_id.product_tmpl_id,lang),

                'Product_attributes': details.get_attribute_product_product(product_id, lang),

                # 'Non_existent_attribute_values': details.find_non_existent_product_combinations(product_id),

            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Product Information'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data found!'}
        return response

    # api get rate
    @http.route(ProductInfo.version + 'latest-dollar-rate', type='json', auth='user', methods=['Post'])
    def get_daily_dollar_rate(self):
        usd_currency = request.env['res.currency'].sudo().search([('name', '=', 'LBP')])
        if usd_currency:
            usd_latest_rate = request.env['res.currency.rate'].sudo().search([('currency_id', '=', usd_currency.id)],
                                                                             order='name desc', limit=1).company_rate
            val = {"last_rate": usd_latest_rate}
            Response.status = '200'
            response = {'status': 200, 'response': val, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Rate found!'}
        return response

    #  get my cart
    @http.route(ProductInfo.version + 'cart', type='json', auth='user', methods=['Post'])
    def get_product_of_cart(self):
        #     get list of products that are added in the cart
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'draft'),
             ('create_uid', '=', request.env.uid)])
        products = []
        cart = []
        Product_Info = ProductInfo()
        if quotation:

            # quotation.get_updated_price()

            for line in quotation.order_line:
                product_info = Product_Info.get_product_product_details(line.product_id)

                # extra_prices = []
                # for attribute_value in line.product_id.product_template_attribute_value_ids:
                #     extra_prices.append (attribute_value.price_extra)
                # base_price = line.product_id.list_price
                # print("Base Price:", base_price)
                # print("Extra Prices:", extra_prices)
                values = {
                    "product_id": line.product_id.id,
                    "product_template_id": line.product_id.product_tmpl_id.id,
                    "product_name": line.product_id.name,
                    "quantity": int(line.product_uom_qty),
                    "price": line.price_unit,
                    # "price": line.product_id.lst_price,
                    # "retailer_price": self.get_retailer_price(line.product_id.product_tmpl_id.id),
                    # "promo_price": self.get_promo_price(line.product_id.product_tmpl_id.id),
                    # 'discount': self.get_retailer_discount(line.product_id.product_tmpl_id.id),
                    # "promo_discount": self.get_promo_discount(line.product_id.product_tmpl_id.id),
                    # "weight": line.product_id.product_tmpl_id.weight,
                    "uom": line.product_id.product_tmpl_id.uom_id.name,
                    "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                    "is_saved": False,
                    "product_info": product_info

                }

                products.append(values)
            cart.append({
                "cart_id": quotation.id,
                "delivery": 0.0,
                'tax': request.env['account.tax'].sudo().search(
                    [('type_tax_use', '=', 'sale'), ('active', '=', True),
                     ('company_id', '=', request.env.company.id)], limit=1).amount,
                "products": products
            })
            Response.status  = '200'
            response = {'status': 200, 'response': {
                "cart_id": quotation.id,
                "delivery": 0.0,
                'tax': request.env['account.tax'].sudo().search(
                    [('type_tax_use', '=', 'sale'), ('active', '=', True),
                     ('company_id', '=', request.env.company.id)], limit=1).amount,
                "products": products
            }, 'message': 'list of cart product'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no product in the cart'}
        return response

    #     add to cart
    @http.route(ProductInfo.version + 'add-to-cart', type='json', auth='user', methods=['Post'])
    def add_product_to_cart(self):

        req = json.loads(request.httprequest.data)
        #         check if there is already quotation opened for this client that is not confirmed as sale order (draft)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'draft'),
             ('create_uid', '=', request.env.uid)])
        product = request.env['product.product'].sudo().search(
            [('id', '=', req.get('product_id'))])
        #         if there is add new line

        if not product:
            Response.status  = '404'
            response = {'status': 404, 'message': 'product not found'}
            return response

        if quotation:
            exist = False

            for line in quotation.order_line:

                if line.product_id.id == product.id:
                    line.product_uom_qty = line.product_uom_qty + req.get('quantity')
                    line.notes = req.get('notes')
                    line.addons_note = req.get('addons_note')
                    line.name = product.name
                    line.removable_ingredients_note = req.get('removable_ingredients_note')
                    exist = True
            if exist == False:
                quotation_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    'name': product.name,
                    "product_uom_qty": req.get('quantity'),
                    "addons_note": req.get('addons_note'),
                    "removable_ingredients_note": req.get('removable_ingredients_note'),
                    # "price_unit": self.get_promo_price(product.id),

                })
        #         if not then create draft quotation
        else:
            quotation_new = request.env['sale.order'].sudo().create({
                "partner_id": retailer_user.partner_id.id,
                "state": 'draft',
                "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
            })
            exist = False
            for line in quotation_new.order_line:
                if line.product_id.id == product.id:
                    line.product_uom_qty = line.product_uom_qty + req.get('quantity')
                    line.notes = req.get('notes')
                    line.addons_note = req.get('addons_note')
                    line.removable_ingredients_note = req.get('removable_ingredients_note')
                    exist = True
            if exist == False:
                quotation_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation_new.id,
                    "product_id": product.id,
                    'name': product.name,
                    "product_uom_qty": req.get('quantity'),
                    "addons_note": req.get('addons_note'),
                    "removable_ingredients_note": req.get('removable_ingredients_note'),

                })
        Response.status  = '200'
        response = {'status': 200, 'message': 'product added to cart'}
        return response

    @http.route(ProductInfo.version + 'remove-from-cart', type='json', auth='user', methods=['Post'])
    def remove_from_cart(self):
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'draft'),
             ('create_uid', '=', request.env.uid)])
        #         if there is draft quotation
        if quotation:
            for line in quotation.order_line:
                #         if the product is in the cart list remove it
                if line.product_id.id == req.get('product_id'):
                    line.unlink()
                if len(quotation.order_line) == 0:
                    quotation.unlink()
            Response.status =  '204'
            response = {'status': 204, 'message': 'product removed from cart'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no product found in the cart'}
        return response




    # all street
    @http.route(ProductInfo.version + 'all-streets', type='json', auth='public', methods=['Post'],cors="*")
    def get_list_of_streets(self):
        streets = request.env['city.street'].sudo().search([])
        list = []
        if streets:
            for street in streets:
                values = {
                    "street_id": street.id,
                    "street_name": street.name
                }
                list.append(values)
            Response.status  = '200'
            response = {'status': 200, 'response': list, 'message': 'list of streets'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no streets found'}
        return response

    # all city
    # get all contact address
    @http.route(ProductInfo.version + 'other-address', type='json', auth='public', methods=['Post'],cors="*")
    def get_list_of_other_address(self):
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        list = []
        if retailer_user.partner_id:
            list.append(
                {
                    "address_id": retailer_user.partner_id.id,
                    "address_name": retailer_user.partner_id.name,
                    "mobile": retailer_user.partner_id.mobile,
                    "phone": retailer_user.partner_id.phone,
                    "street_id": retailer_user.partner_id.street_id.id,
                    "street_name": retailer_user.partner_id.street_id.name,
                    "city_id": retailer_user.partner_id.city_id.id,
                    "city_name": retailer_user.partner_id.city_id.name,
                    "state_id": retailer_user.partner_id.state_id.id,
                    "state_name": retailer_user.partner_id.state_id.name,
                    "near": retailer_user.partner_id.street2,
                    "lat": retailer_user.partner_id.partner_latitude,
                    "long": retailer_user.partner_id.partner_longitude,
                    "can_delete": False
                }
            )
            if retailer_user.partner_id.child_ids:
                for add in retailer_user.partner_id.child_ids:
                    values = {
                        "address_id": add.id,
                        "address_name": add.name,
                        "mobile": add.mobile,
                        "phone": add.phone,
                        "street_id": add.street_id.id,
                        "street_name": add.street_id.name,
                        "city_id": add.city_id.id,
                        "city_name": add.city_id.name,
                        "state_id": add.state_id.id,
                        "state_name": add.state_id.name,
                        "near": add.street2,
                        "lat": add.partner_latitude,
                        "long": add.partner_longitude,
                        "can_delete": True
                    }
                    list.append(values)

            Response.status  = '200'
            response = {'status': 200, 'response': list, 'message': 'list other address'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no other address found'}
        return response
        # get contact address id

    @http.route(ProductInfo.version + 'address-information', type='json', auth='public', methods=['Post'],cors="*")
    def get_other_address_by_id(self):
        req = json.loads(request.httprequest.data)
        address = request.env['res.partner'].sudo().search([('id', '=', req.get("address_id"))])
        if address:
            values = {
                "address_name": address.name,
                "mobile": address.mobile,
                "phone": address.phone,
                "street_id": address.street_id.id,
                "street_name": address.street_id.name,
                "city_id": address.city_id.id,
                "city_name": address.city_id.name,
                "state_id": address.state_id.id,
                "state_name": address.state_id.name,
                "near": address.street2,
                "lat": address.partner_latitude,
                "long": address.partner_longitude
            }
            Response.status  = '200'
            response = {'status': 200, 'response': values, 'message': 'address information'}

        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no address found'}
        return response

    # add address contact
    @http.route(ProductInfo.version + 'add-other-address', type='json', auth='public', methods=['Post'],cors="*")
    def add_other_address(self):

        # retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        # boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])
        # street = request.env['city.street'].sudo().search([('id', '=', req.get('street_id'))])
        # line = request.env['zone.lines'].sudo().search([('streets', '=', req.get('street_id'))])
        if retailer_user:
            if req.get('city'):
                address =req.get('city')
            else:
                address = ''
            
            if req.get('street'):
                if address!='':
                    address =address + ' - ' + req.get('street')
                else:
                    address = req.get('street')
            
            if req.get('near'):
                if address!='':
                    address =address + ' - ' + req.get('near')
                else:
                    address = req.get('near')


            try:
                free_delivery = retailer_user.partner_id.free_delivery
            except:
                free_delivery = False
            detail = ProductInfo()
            val_zone = detail.calcul_for_address(req.get('lat'), req.get('long'), False, free_delivery)
            address_in_zone = False
            if val_zone:
                address_in_zone = True
                zone_id = val_zone['zone_id']
            else:
                address_in_zone = False
                zone_id = None
            values = {
            "name": req.get('name'),
            "mobile": req.get('mobile'),
            "phone": req.get('phone'),
            # "street_id": req.get('street_id'),
            # "city_id": street.city_id.id,
            "city": req.get('city') if req.get('city') else "",
            "street": req.get('street') if req.get('street') else "",
            "street2": req.get('near') if req.get('near') else "",
            "partner_latitude": req.get('lat'),
            "partner_longitude": req.get('long'),
            "parent_id": retailer_user.partner_id.id,
            "is_client": True,
            # "is_member": False,
            "is_driver": False,
            "is_manager": False,
            "type": 'delivery',
            "zone_id": zone_id , #|req.get('zone_id') if req.get('zone_id') else None,
            # "state_id": street.city_id.state_id.id,
            # "country_id": street.city_id.state_id.country_id.id
            }
    
            new_address = request.env['res.partner'].sudo().create(values)
    
    
            # new_address.write({"street2":req.get('near')})
            if new_address:
                Response.status =  '201'
                message = ''
                if address_in_zone:
                    message = 'New Address created'
                else:
                    message = 'New Address created. Out of Zone'
                response = {'status': 201, 'response': new_address.id, 'message': message}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'Address not added'}
                
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User not Found'}
        return response

    # update address
    @http.route(ProductInfo.version + 'update-other-address', type='json', auth='public', methods=['Post'],cors="*")
    def update_other_address(self):
        req = json.loads(request.httprequest.data)
        address = request.env['res.partner'].sudo().search([('id', '=', req.get('address_id'))])
        if address:
            values = {
                "name": req.get('name'),
                "mobile": req.get('mobile'),
                "phone": req.get('phone'),
                "street_id": req.get('street_id'),
                "street2": req.get('near'),
                "partner_latitude": req.get('lat'),
                "partner_longitude": req.get('long'),
            }
            address.sudo().update(values)
            Response.status =  '202'
            response = {'status': 202, 'message': 'Address updated'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'Address not found'}
        return response

    # remove contact address
    @http.route(ProductInfo.version + 'remove-other-address', type='json', auth='public', methods=['Post'], cors="*")
    def remove_other_address(self):
        req = json.loads(request.httprequest.data)
        address = request.env['res.partner'].sudo().search([('id', '=', req.get("address_id"))])
        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])
        if user:
            if address:
                if user.partner_id.id != address.id:
                    for user_address in user.partner_id.child_ids:
                        if user_address == address:
                            try:
                                address.sudo().unlink()
                                Response.status = '200'
                                response = {'status': 200,'success':True, 'message': 'Address removed'}
                                return response
                            except:
                                Response.status = '200'
                                response = {'status': 200,'success':False, 'message': 'Address Used Can not be removed!'}
                                return response

                    Response.status = '404'
                    response = {'status': 404, 'message': 'Address not found in user addresses list'}
                else:
                    Response.status = '200'
                    response = {'status': 200,'success':False, 'message': 'Address can not be removed!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Address not found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User not found'}
        return response

    
    @http.route(ProductInfo.version + 'orders-history', type='json', auth='public', methods=['Post'],cors='*')
    def get_history_orders(self):
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if retailer_user:

            # quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],order='create_date Desc')


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
                                "notes":the_notes if the_notes else "",
                                "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total/int(line.product_uom_qty),2)
                            }
                            products.append(values)
                            
                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id":order.sale_order_type,
                            "delivery_fees":delivery_charge,
                            "order_date": order.date_order.date(),
                            "amount":order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status":order_status,
                            "order_status_id":"7",
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
        return response

    @http.route(ProductInfo.version + 'current-orders', type='json', auth='public', methods=['Post'] ,cors='*')
    def get_current_orders(self):
        req = json.loads(request.httprequest.data)
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        if retailer_user:
            # sale_orders_delivered = quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '=', '7')],order='create_date Desc')

            # quotations = request.env['sale.order'].sudo().search(
            #     [('partner_id', '=', retailer_user.partner_id.id), ('order_status', '!=', '7'),('state', '!=', 'cancel')],
            #     order='create_date Desc')

            if lang == "ar":
                quotations = request.env['sale.order'].with_context(lang='ar_001').sudo().search([('partner_id', '=', retailer_user.partner_id.id),('sale_order_type', '!=', '3'), ('order_status', '!=', '7'),('state', '!=', 'cancel')],order='create_date Desc')
            else:
                quotations = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', retailer_user.partner_id.id),('sale_order_type', '!=', '3'), ('order_status', '!=', '7'),('state', '!=', 'cancel')],
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
                    if saved_location==False:
                        if order.order_status =='5' or order.order_status =='6':
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
                                "notes":the_notes if the_notes else "",
                                "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                                "quantity": int(line.product_uom_qty),
                                "price": round(line.price_total/int(line.product_uom_qty),2)
                            }
                            products.append(values)
                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id":order.sale_order_type,
                            "delivery_fees":delivery_charge,
                            "order_date": order.date_order.date(),
                            "amount": order.amount_total,
                            "currency_symbol": order.company_id.currency_id.name,
                            "currency_symbol_en": order.company_id.currency_id.name,
                            "order_status": order_status,
                            "order_status_id":order_status_id,
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
        return response

    @http.route(ProductInfo.version + 'current-order-details', type='json', auth='public', methods=['Post'], cors='*')
    def get_current_order_details(self):
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
                    orders.append(
                        {
                            "order_id": order.id,
                            "order_name": order.name,
                            "sale_order_type_id": order.sale_order_type,
                            "delivery_fees": delivery_charge,
                            "order_date": order.date_order.date(),
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
        return response
    #     get all retailer orders
    @http.route(ProductInfo.version + 'orders', type='json', auth='user', methods=['Post'])
    def get_all_retailer_orders(self):
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        quotations = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'sale'),
             ('create_uid', '=', request.env.uid)])
        orders = []
        trip_id = 0
        status = "Order Received"
        Product_Info = ProductInfo()
        if quotations:
            for order in quotations:
                if order.state == "sale":
                    for line in order.picking_ids:
                        if line.state == "done" and ('PICK' in line.name):
                            status = "Ready For Dispatch"
                            trip_id = request.env['orders.trip'].sudo().search([('stock_picking_ids', 'in', line.id)],
                                                                               order='create_date desc', limit=1)
                            if trip_id != 0:
                                if trip_id.status == "done_ovb" or trip_id.status == "done":
                                    status = "Out for delivery"
                                    if (line.start_date != False) and (line.end_date != False):
                                        status = "Delivered"
                                    elif line.start_date != False:
                                        status = "On the way"
                products = []
                for line in order.order_line:
                    values = {
                        "product_id": line.product_id.product_tmpl_id.id,
                        "product_name": line.product_id.product_tmpl_id.name,
                        "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                        "quantity": int(line.product_uom_qty),
                        "price": line.price_unit
                    }
                    products.append(values)
                orders.append(
                    {
                        "order_id": order.id,
                        "order_name": order.name,
                        "order_date": order.date_order.date(),
                        "order_number": order.id,
                        "shipment_status": status,
                        "shipment_address_id": order.partner_shipping_id.id,
                        "products": products
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': orders, 'message': 'list of orders found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no orders found'}
        return response

    #     get retailer order by id
    @http.route(ProductInfo.version + 'order-id', type='json', auth='user', methods=['Post'])
    def get_retailer_order_by_id(self):
        req = json.loads(request.httprequest.data)
        quotations = request.env['sale.order'].sudo().search(
            [('id', '=', req.get('order_id'))])
        products = []
        orders = []
        trip_id = 0
        status_id = 2
        status = "Order Received"
        Product_Info = ProductInfo()
        if quotations:
            for order in quotations:
                if order.state == "sale":
                    for line in order.picking_ids:
                        if line.state == "done" and ('PICK' in line.name):
                            status_id = 3
                            status = "Ready For Dispatch"
                            trip_id = request.env['orders.trip'].sudo().search([('stock_picking_ids', 'in', line.id)],
                                                                               order='create_date desc', limit=1)
                            if trip_id != 0:
                                if trip_id.status == "done_ovb" or trip_id.status == "done":
                                    status_id = 4
                                    status = "Out for delivery"
                                    if (line.start_date != False) and (line.end_date != False):
                                        status_id = 6
                                        status = "Delivered"
                                    elif line.start_date != False:
                                        status_id = 5
                                        status = "On the way"
                for line in order.order_line:
                    values = {
                        "product_id": line.product_id.product_tmpl_id.id,
                        "product_name": line.product_id.product_tmpl_id.name,
                        "product_uom": line.product_id.uom_id.id,
                        "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                        "quantity": int(line.product_uom_qty),
                        "price": line.price_unit,
                        "barcode": line.product_id.product_tmpl_id.barcode,
                    }
                    products.append(values)
                urls = []
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        if invoice.state == 'posted':
                            n = str(invoice.name) + ".pdf"
                            report = request.env['ir.attachment'].sudo().search(
                                [('res_name', '=', invoice.name), ('name', '=', n),
                                 ('res_model', '=', 'account.move'), ('public', '=', True),
                                 ('mimetype', '=', 'application/pdf')])
                            # URL = report.datas
                            urls.append({"invoice_name": invoice.name,
                                         "link": report.datas,
                                         })
                orders.append(
                    {
                        "order_id": order.id,
                        "order_name": order.name,
                        "invoices": urls,
                        "order_date": order.date_order.date(),
                        "order_number": order.id,
                        "shipment_status": status,
                        "shipment_status_id": status_id,
                        "shipment_address_id": order.partner_shipping_id.id,
                        "delivery_charge": 0.0,
                        "products": products
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': {
                "order_id": order.id,
                "order_name": order.name,
                "invoices": urls,
                "order_date": order.date_order.date(),
                "order_number": order.id,
                "shipment_status": status,
                "shipment_status_id": status_id,
                "shipment_address_id": order.partner_shipping_id.id,
                "shipment_address_name": order.partner_shipping_id.name,
                "delivery_charge": 0.0,
                "products": products
            }, 'message': 'list of orders found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no orders found'}
        return response

    #     checkout order
    @http.route(ProductInfo.version + 'checkout', type='json', auth='user', methods=['Post'])
    def checkout_order(self):
        #         found out the draft quotation then confirm the quotation and add shipping id
        req = json.loads(request.httprequest.data)
        quotation = request.env['sale.order'].sudo().search([('id', '=', req.get('order_id'))])
        retailer = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        if quotation:
            quotation.update({
                "partner_shipping_id": req.get("address_id")
            })

            quotation.action_confirm()
            # notifications_saved = request.env['sent.notification'].sudo().create({
            #     "name": "Your Order has been confirmed!",
            #     "description": "Your order " + str(quotation.name) + " has been confirmed",
            #     "users": [(4, retailer.id)],
            #     "order_id": quotation.id,
            #     "notif_type": 'order_confirmed_11'
            # })
            # server_Token = 'AAAAkbO6iY8:APA91bFjrWKifQeAejeZU9P4qbs2j9Rkg3JLZRHVGRls_9e8etbzCYRiVtAyyvhKMc-HXHEGxAvqitIt4NBvOeuxEBXI4i-aCI08PDWQrnXsKL4XxNxG_EGq_VTm_Q5Q-2VIVwsV5MzF'
            # device_Token = retailer.user_token
            # headers = {
            #     'Content-Type': 'application/json',
            #     'Authorization': 'key=' + server_Token,
            # }
            # body = {
            #     'notification': {'title': "Your Order has been confirmed!",
            #                      'body': "Your order " + str(quotation.name) + " has been confirmed",
            #                      },
            #     'to':
            #         device_Token,
            #     'priority': 'high',
            #     "data": {
            #         "sender_id": 3,
            #         "type_id": 11,
            #         "order_id": notifications_saved.order_id.id,
            #         "type_name": dict(notifications_saved._fields['notif_type'].selection).get(
            #             notifications_saved.notif_type),
            #     },
            # }
            #
            # notif = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
            Response.status  = '200'
            response = {'status': 200, 'message': 'Order Confirmed'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no orders found'}
        return response

    #     retailer profile
    @http.route(ProductInfo.version + 'profile', type='json', auth='user', methods=['Post'])
    def retailer_profile(self):
        all = []
        retailer = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        user_zone = request.env['zone.zone'].sudo().search([('id', '=', retailer.partner_id.zone_id.id)])
        if retailer.partner_id or user_zone:
            values = {
                'zone_id': retailer.partner_id.zone_id.name,
                'name': retailer.partner_id.name,
                'state': retailer.partner_id.state_id.name,
                'city': retailer.partner_id.city_id.name,
                'street': retailer.partner_id.street_id.name
            }
            all.append(values)
            response = {'status': 200, 'response': all, 'message': 'Success'}
        else:
            response = {'status': 404, 'message': 'No data Found!'}
        return response


    @http.route(ProductInfo.version + 'product-information-barcode', type='json', auth='public', methods=['Post'],cors="*")
    def get_product_information_by_barcode(self):
        details = ProductInfo()
        req = json.loads(request.httprequest.data)
        products = []
        for barcode in req.get('barcodes'):
            product_id = request.env['product.template'].sudo().search([('barcode', '=', barcode['serial'])])
            retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
            all_wishlist = request.env['product.wishlist'].sudo().search(
                [('partner_id', '=', retailer_user.partner_id.id)])
            if product_id:
                images = request.env['product.image'].sudo().search([('product_tmpl_id', '=', product_id.id)])
                images_list = []
                images_list.append("/web/content/" + str(product_id.image_attachment.id))
                for image in images:
                    images_list.append("/web/content/" + str(image.image_attachment.id))
                codes = []
                # same_similar_code = request.env['product.template'].sudo().search(
                #     [('similar_code', '=', product_id.similar_code.id)])
                # for p in same_similar_code:
                #     same_similar_code_same_unit = request.env['product.template'].sudo().search(
                #         [('similar_code', '=', product_id.similar_code.id), ('unit_code', '=', p.unit_code.id)])
                #     if {
                #         'unit': p.unit_code.name,
                #
                #         'products_id': [({"product_id": line.id,
                #                           "name": line.pack_of_id.name,
                #                           "unit_price": line.list_price,
                #                           "retailer_price": self.get_retailer_price(line.id),
                #                           "promo_price": self.get_promo_price(line.id)}) for line in
                #                         same_similar_code_same_unit],
                #     } not in codes:
                #         codes.append(
                #             {
                #                 'unit': p.unit_code.name,
                #                 'products_id': [({"product_id": line.id,
                #                                   "name": line.pack_of_id.name,
                #                                   "unit_price": line.list_price,
                #                                   "retailer_price": self.get_retailer_price(line.id),
                #                                   "promo_price": self.get_promo_price(line.id)}) for line in
                #                                 same_similar_code_same_unit],
                #             }
                #         )
                is_fav = False
                for wish in all_wishlist:
                    if product_id.id == wish.product_template_id.id:
                        is_fav = True
                        break
                values = {
                    "product_name": product_id.name,
                    "product_description": details.change_parag_to_line(product_id.description_sale),
                    "product_image": "/web/content/" + str(product_id.image_attachment.id) if product_id.image_attachment.id else "",
                    "product_images": images_list,
                    'is_fav': is_fav,
                    'pack': codes,
                    'price': product_id.list_price,
                    # "retailer_price": self.get_retailer_price(product_id.id),
                    # "promo_price": self.get_promo_price(product_id.id),
                    # 'discount': self.get_retailer_discount(product_id.id),
                    # "promo_discount": self.get_promo_discount(product_id.id),
                }
                products.append(values)
        if products:
            Response.status  = '200'
            response = {'status': 200, 'response': products, 'message': 'Product Information'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'No data found!'}
        return response

    # update cart
    @http.route(ProductInfo.version + 'update-cart', type='json', auth='user', methods=['Post'])
    def update_cart_item(self):
        req = json.loads(request.httprequest.data)
        quotation = request.env['sale.order'].sudo().search([('id', '=', req.get('cart_id'))])
        if quotation:
            for line in quotation.order_line:
                if line.product_id.id == req.get('product_id'):
                    values = {
                        "product_uom_qty": req.get('quantity'),
                    }
                    line.update(values)
            Response.status =  '202'
            response = {'status': 202, 'message': 'item cart updated'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'product not found in cart'}
        return response

    @http.route(ProductInfo.version + 'update-wishlist', type='json', auth='public', methods=['Post'],cors='*')
    def update_wishlist(self):
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if retailer_user:
                if req.get('fav') == True:
                    product_id = request.env['product.product'].sudo().search([('id', '=', req.get('product_id'))])
                    exist = request.env['product.wishlist'].sudo().search(
                        [('partner_id', '=', retailer_user.partner_id.id), ('product_id', '=', product_id.id)])
                    if exist:
                        Response.status  = '200'
                        response = {'status': 200, 'message': 'Product added to wishlist!'}
                        return response

                    if product_id:

                        wishlist_created = request.env['product.wishlist'].sudo().create(
                            {"partner_id": retailer_user.partner_id.id,
                             "product_id": product_id.id,
                             "product_template_id": product_id.product_tmpl_id.id,
                             "website_id": 1
                             }
                        )
                        if wishlist_created:
                            Response.status  = '200'
                            response = {'status': 200, 'response': wishlist_created.id, 'message': 'Wishlist Created'}
                        else:
                            Response.status  = '404'
                            response = {'status': 404, 'message': 'Not Added!'}
                    else:
                        Response.status  = '404'
                        response = {'status': 404, 'message': 'Product Not Found!'}

                else:
                    product_wishlist_id = request.env['product.wishlist'].sudo().search(
                        [('product_id', '=', req.get('product_id')), ('partner_id', '=', retailer_user.partner_id.id)])
                    if product_wishlist_id:
                        product_wishlist_id.unlink()
                        Response.status  = '200'
                        response = {'status': 200, 'message': 'Product removed from wishlist!'}
                    else:
                        Response.status  = '404'
                        response = {'status': 404, 'message': 'Product Not Found!'}
            else:
                Response.status  = '404'
                response = {'status': 404, 'message': 'User Not Found!'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        return response

   

    @http.route(ProductInfo.version + 'receive-return-order', type='json', auth='user', methods=['Post'])
    def receive_return_order(self):
        req = json.loads(request.httprequest.data)
        quotation = request.env['sale.order'].sudo().search([('id', '=', req.get('order_id'))])
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        if quotation and quotation.partner_id.id == retailer_user.partner_id.id:
            quotation.is_confirmed = True
            returns = []
            for line in quotation.order_line:
                for product in req.get("products"):
                    if line.product_id.product_tmpl_id.id == product['product_id']:
                        line.qty_delivered = product['quantity']
                        if line.qty_delivered != line.product_uom_qty:
                            returns.append({
                                "product_id": line.product_id.id,
                                "quantity_to_return": line.product_uom_qty - line.qty_delivered,
                                "product_uom": product['product_uom'],
                                "return_reason": product['return reason']
                            })
                if returns:
                    for pick in quotation.picking_ids:
                        if 'OUT' in pick.name:
                            is_warehouse = retailer_user.partner_id.zone_id.warehouse_id.id
                            operation_type = request.env['stock.picking.type'].sudo().search(
                                [('name', '=', 'Returns'), ('warehouse_id', '=', is_warehouse)])

                            return_order = request.env['stock.picking'].sudo().create({
                                "origin": _("Return of %s") % pick.name,
                                "sale_id": quotation.id,
                                'picking_type_id': operation_type.id,
                                'partner_id': retailer_user.partner_id.id,
                                'location_id': operation_type.default_location_src_id.id if operation_type.default_location_src_id.id else 1,
                                'location_dest_id': operation_type.default_location_dest_id.id,
                                'move_ids_without_package': [(0, None, {
                                    'product_id': line['product_id'],
                                    'name': "name",
                                    'product_uom_qty': line['quantity_to_return'],
                                    'product_uom': line['product_uom'],
                                    'location_id': operation_type.default_location_src_id.id if operation_type.default_location_src_id.id else 1,
                                    'location_dest_id': operation_type.default_location_dest_id.id,
                                    'return_reason': "1" if line['return_reason'] == 1 else "2"
                                }) for line in returns]
                            })
            Response.status  = '200'
            response = {'status': 204, 'message': 'Order Delivered'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no data found'}
        return response

    @http.route(ProductInfo.version + 'also-like-products', type='json', auth='public', methods=['Post'],cors="*")
    def get_also_like_product(self):
        req = json.loads(request.httprequest.data)
        product = request.env['product.template'].sudo().search(
            [('id', '=', req.get('product_id'))])
        products = []
        Product_Info = ProductInfo()
        if product:
            for cross in product.accessory_product_ids:

                try:
                    res = cross.taxes_id.compute_all(cross.lst_price, product=cross)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = cross.lst_price

                products.append(
                    {
                        "product_id": cross.product_tmpl_id.id,
                        "product_name": cross.product_tmpl_id.name,
                        "product_image": "/web/content/" + str(cross.product_tmpl_id.image_attachment.id) if cross.product_tmpl_id.image_attachment.id else "",
                        "price": Product_Info.get_product_product_price(cross,price_product),
                        # "price": cross.product_tmpl_id.list_price,
                        # "retailer_price": self.get_retailer_price(cross.product_tmpl_id.id),
                        # "promo_price": self.get_promo_price(cross.product_tmpl_id.id),
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': products, 'message': 'cross products found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no products!'}
        return response


    @http.route(ProductInfo.version + 'related-products', type='json', auth='public', methods=['Post'], cors="*")
    def get_optional_product(self):
        req = json.loads(request.httprequest.data)
        product = request.env['product.template'].sudo().search(
            [('id', '=', req.get('product_id'))])
        products = []
        Product_Info = ProductInfo()
        if product:
            for relt in product.optional_product_ids:
                products.append(
                    {
                        "product_id": relt.id,
                        "product_name": relt.name,
                        "product_image": "/web/content/" + str(relt.image_attachment.id) if relt.image_attachment.id else "",
                        "price": Product_Info.get_product_template_price (relt),
                        # "price": relt.list_price,
                        # "retailer_price": self.get_retailer_price(relt.id),
                        # "promo_price": self.get_promo_price(relt.id),
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': products, 'message': 'related products found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no products!'}
        return response



    @http.route(ProductInfo.version + 'addons-products', type='json', auth='public', methods=['Post'],cors="*")
    def get_addons_product(self):
        req = json.loads(request.httprequest.data)
        product = request.env['product.template'].sudo().search(
            [('id', '=', req.get('product_id'))])
        products = []
        Product_Info = ProductInfo()
        if product:
            for addon in product.product_addons_ids:
                try:
                    res = addon.taxes_id.compute_all(addon.lst_price, product=addon)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = addon.lst_price
                products.append(
                    {
                        "product_id": addon.id,
                        "product_name": addon.name,
                        "product_image": "/web/content/" + str(addon.product_tmpl_id.image_attachment.id) if addon.product_tmpl_id.image_attachment.id else "",
                        "price": Product_Info.get_product_product_price (addon,price_product),
                        # "price": addon.product_tmpl_id.list_price,
                        # "retailer_price": self.get_retailer_price(addon.product_tmpl_id.id),
                        # "promo_price": self.get_promo_price(addon.product_tmpl_id.id),
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': products, 'message': 'related products found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no products!'}
        return response

    @http.route(ProductInfo.version + 'removable-ingredients', type='json', auth='public', methods=['Post'],cors="*")
    def get_removable_ingredients(self):
        req = json.loads(request.httprequest.data)
        product = request.env['product.template'].sudo().search(
            [('id', '=', req.get('product_id'))])
        products = []
        Product_Info = ProductInfo()
        if product:
            for removable in product.removable_ingredient_ids:
                try:
                    res = removable.taxes_id.compute_all(removable.lst_price, product=removable)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = removable.lst_price
                products.append(
                    {
                        "product_id": removable.product_tmpl_id.id,
                        "product_name": removable.product_tmpl_id.name,
                        "product_image": "/web/content/" + str(removable.product_tmpl_id.image_attachment.id) if removable.product_tmpl_id.image_attachment.id else "",
                        "price": Product_Info.get_product_product_price(removable,price_product),
                        # "price": removable.product_tmpl_id.list_price,
                        # "retailer_price": self.get_retailer_price(removable.product_tmpl_id.id),
                        # "promo_price": self.get_promo_price(removable.product_tmpl_id.id),
                    }
                )
            Response.status  = '200'
            response = {'status': 200, 'response': products, 'message': 'cross products found'}
        else:
            Response.status  = '404'
            response = {'status': 404, 'message': 'no products!'}
        return response


    @http.route(ProductInfo.version + 'returns', type='json', auth='user', methods=['Post'])
    def get_returns_products(self):
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        # quotations = request.env['sale.order'].sudo().search(
        #     [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'sale')])
        returns_orders = request.env['stock.picking'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('name', 'ilike', 'RET')])
        returns = []
        products = []
        Product_Info = ProductInfo()
        if returns_orders:
            for ret in returns_orders:
                for line in ret.move_ids_without_package:
                    products.append({
                        "product_id": line.product_id.product_tmpl_id.id,
                        "product_name": line.product_id.product_tmpl_id.name,
                        "return_reason": line.return_reason,
                        "price": Product_Info.get_product_template_price(line.product_id.product_tmpl_id),
                        # "price": line.product_id.product_tmpl_id.list_price,
                        # "retailer_price": self.get_retailer_price(line.product_id.product_tmpl_id.id),
                        # "promo_price": self.get_promo_price(line.product_id.product_tmpl_id.id),
                        "product_image": "/web/content/" + str(line.product_id.product_tmpl_id.image_attachment.id) if line.product_id.product_tmpl_id.image_attachment.id else "",
                    })
                if {
                    "order_id": ret.sale_id.id,
                    "order_name": ret.sale_id.name,
                    "address_id": ret.sale_id.partner_shipping_id.id,
                    "address_name": ret.sale_id.partner_shipping_id.name,
                    "date": ret.sale_id.date_order.date(),
                    "phone": ret.partner_id.mobile,
                    "products": products
                } not in returns:
                    returns.append({
                        "order_id": ret.sale_id.id,
                        "order_name": ret.sale_id.name,
                        "address_id": ret.sale_id.partner_shipping_id.id,
                        "address_name": ret.sale_id.partner_shipping_id.name,
                        "date": ret.sale_id.date_order.date(),
                        "phone": ret.partner_id.mobile,
                        "products": products
                    })
            Response.status = '200'
            response = {'status': 200, 'response': returns, 'message': 'returned orders found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no returns!'}
        return response

    @http.route(ProductInfo.version + 'loyalty', type='json', auth='user', methods=['Post'])
    def get_retailer_loyalty_points(self):
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        retailer_history = request.env['loyalty.history'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id)])
        points = []
        Product_Info = ProductInfo()
        if retailer_history:
            for loy in retailer_history:
                points.append({
                    "date": loy.date,
                    "payment": loy.payment_id.name,
                    "invoice": loy.payment_id.cheque_reference,
                    "status": dict(loy._fields['transaction_type'].selection).get(loy.transaction_type),
                    "payment_amount": loy.payment_amount,
                    "points": loy.points
                })
            values = {
                "loyalty_points": retailer_user.partner_id.loyalty_points,
                "loyalty_history": points
            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'retailer points found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no points found!'}
        return response

    @http.route(ProductInfo.version + 'place-order-public', type='json', auth='public', methods=['Post'], cors="*")
    def place_order_public(self):
        Product_Info = ProductInfo()
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
                        response = {'status': 404, 'message': 'Product Not Found'}
                        return response
                    try:
                        res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                        included = res['total_included']
                        price_product = included
                    except:
                        price_product = product_addon.lst_price
                    if addon['price'] != Product_Info.get_product_product_price(product_addon):
                        Response.status = '404'
                        
                        response = {'status': 404, 'message': 'Add On Price Not Correct'}
                        return response
                    addon_price = addon_price + addon['price']

            price_unit = record['price']

            try:
                res = product.taxes_id.compute_all(product.lst_price, product=product)
                included = res['total_included']
                price_product = included
            except:
                price_product = product.lst_price


            if (price_unit - addon_price) != Product_Info.get_product_product_price(product):
                Response.status = '404'
                
                response = {'status': 404, 'message': 'Price Not Correct'}
                return response

        company_id = req.get('company_id')

        boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

        user_timezone = boot.tz


        delivery_date_str = req.get('delivery_date')

        date_format = "%d/%m/%Y %H:%M:%S"
        delivery_date = datetime.strptime(delivery_date_str, date_format)

        source_timezone = pytz.timezone('UTC')  # Replace 'UTC' with the actual source timezone

        delivery_date = pytz.timezone(user_timezone).localize(delivery_date).astimezone(source_timezone)

        delivery_date_naive = delivery_date.replace(tzinfo=None)

        # if req.get('sale_order_type_id')=='1':
        quotation = request.env['sale.order'].sudo().create({
            "partner_id":req.get('address_id'),
            "state": 'draft',
            "company_id": company_id,
            "delivery_date": delivery_date_naive,
            "sale_order_type": req.get('sale_order_type_id'),
            "partner_shipping_id": req.get('address_id'),
            "user_id":boot.id,
            # "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
        })
        # else:
        #     quotation = request.env['sale.order'].sudo().create({
        #         "partner_id": boot.partner_id.id,
        #         "state": 'draft',
        #         "company_id": company_id,
        #         "delivery_date": delivery_date_naive,
        #         "sale_order_type": req.get('sale_order_type_id'),
        #         "user_id": boot.id,
        #         # "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
        #     })
            
        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])

            price = product.lst_price
            addons = record['addons_note']
            addon_price = 0
            if addons:
                addon_price = 0
                for addon in addons:
                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])

                    # addon_price = addon_price + addon['price']
                    price = price + product_addon.lst_price
            if product:
                request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    # "price_unit": price ,
                    "price_unit": record['price'] + addon_price ,
                    # "price_total": record['totlal_price_product'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    # "price_unit": self.get_promo_price(product.id)
                })
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response
        
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

        return response

    @http.route(ProductInfo.version + 'place-order-user-old', type='json', auth='public', methods=['Post'], cors="*")
    def place_order_user(self):
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        zone_id = req.get('zone_id')
        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if user:
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
                        try:
                            res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                            included = res['total_included']
                            price_product = included
                        except:
                            price_product = product_addon.lst_price
                        if addon['price'] != Product_Info.get_product_product_price(product_addon):
                            Response.status = '404'

                            response = {'status': 404, 'message': 'Add On Price Not Correct'}
                            return response
                        addon_price = addon_price + addon['price']

                price_unit = record['price']

                try:
                    res = product.taxes_id.compute_all(product.lst_price, product=product)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = product.lst_price

                if round((price_unit - addon_price),3) != round(Product_Info.get_product_product_price(product),3):
                    Response.status = '404'

                    response = {'status': 404, 'message': 'Price Not Correct'}
                    return response
        else:
            Response.status = '404'

            response = {'status': 404, 'message': 'User Not Found'}
            return response


        company_id = req.get('company_id')

        # boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

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
        if req.get('sale_order_type_id')=='1':
            thepartner_id = req.get('address_id')
        else:
            thepartner_id = user.partner_id.id
            
        quotation = request.env['sale.order'].sudo().create({
            "partner_id": user.partner_id.id,
            "state": 'draft',
            "company_id": company_id,
            "delivery_date": delivery_date_naive,
            "sale_order_type": req.get('sale_order_type_id'),
            "partner_shipping_id": thepartner_id,
            "user_id": user.id,
            "zone_id":zone_id
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
                request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    "price_unit": price,
                    # "price_unit": record['price'] + addon_price,
                    # "price_total": record['totlal_price_product'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    # "price_unit": self.get_promo_price(product.id)
                })
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response

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

        managers = request.env['res.partner'].sudo().search([('is_manager','=','True'),('company_id','=',company_id)])
        if managers:
            for manager in managers:
                manager_user = request.env['res.users'].sudo().search([('partner_id','=',manager.id)])
                if manager_user:
                    notification.send_notification(request.env.user, manager_user, message_name, message_description,
                                            quotation.id)

        # except:
        #     pass
        return response

    @http.route(ProductInfo.version + 'place-order-user', type='json', auth='public', methods=['Post'], cors="*")
    def place_order_user_new(self):
        Product_Info = ProductInfo()
        # FirstOrder_Discount = FirstOrderDiscount()
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
                if company.disable_users :
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
        if user:
            # first = FirstOrder_Discount.get_first_order_discount_local(user)

            for record in req.get('products'):
                product = request.env['product.product'].sudo().search(
                    [('id', '=', record['product_id'])])


                if len(product) == 0:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Product Not Found','product_id':record['product_id']}
                    return response
                
                if product.app_publish == False:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Product Not Available','product_id':record['product_id'],'product_name':product.name}
                    return response

                addons = []
                addons = record['addons_note']
                addon_price = 0
                if addons:
                    addon_price = 0
                    for addon in addons:

                        product_addon = request.env['product.product'].sudo().search(
                            [('id', '=', addon['product_id'])])
                        if len(product_addon) == 0 :
                            Response.status = '404'
                            response = {'status': 404, 'message': 'Add On Not Found','add_on_id':addon['product_id']}
                            return response

                        # if product_addon.app_publish == False:
                        #     Response.status = '404'
                        #     response = {'status': 404, 'message': 'Add On Not Available',
                        #                 'product_id': addon['product_id'], 'product_name': product_addon.name}
                        #     return response

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
                                        'final_price_Without_TVA' : values['final_price_Without_TVA'],
                                        'final_price':values['final_price']}
                            return response
                        addon_price = addon_price + addon['price']

                price_unit = record['price']

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
                                'product_id':product.id,'product_name':product.name,
                                'final_price_Without_TVA' : values['final_price_Without_TVA'],
                                'final_price':values['final_price']}
                    return response
        else:
            Response.status = '404'

            response = {'status': 404, 'message': 'User Not Found'}
            return response



        # boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

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

        try:
            quotation = request.env['sale.order'].sudo().create({
                "partner_id": user.partner_id.id,
                "state": 'draft',
                "company_id": company_id,
                "delivery_date": delivery_date_naive,
                "sale_order_type": req.get('sale_order_type_id'),
                "partner_shipping_id": thepartner_id,
                "user_id": user.id,
                "zone_id": zone_id,
                "discount_type": "percent",
                "discount_rate": discount
            })
        except:
            quotation = request.env['sale.order'].sudo().create({
                "partner_id": user.partner_id.id,
                "state": 'draft',
                "company_id": company_id,
                "delivery_date": delivery_date_naive,
                "sale_order_type": req.get('sale_order_type_id'),
                "partner_shipping_id": thepartner_id,
                "user_id": user.id,
                "zone_id": zone_id
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
                order_line = request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    # "price_unit": price,
                    "price_unit": record['price'] ,
                    # "price_total": record['totlal_price_product'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    # "price_unit": self.get_promo_price(product.id)
                })
                order_line.with_context(lang='ar_001').update({'kitchen_notes': Product_Info.create_kitchen_notes_new(record['notes'],record['addons_note'],record['removable_ingredients_note'],record['combo_content'],"ar",product)})
                order_line.update({'kitchen_notes': Product_Info.create_kitchen_notes_new(record['notes'],record['addons_note'],record['removable_ingredients_note'],record['combo_content'],"en",product)})

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response
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
        # quotation.sudo().write(
        #     {
        #         "discount_type":"percent",
        #         "discount_rate":discount
        #     }
        #
        # )

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



    @http.route(ProductInfo.version + 'validate-order', type='json', auth='public', methods=['Post'], cors="*")
    def validate_order(self):
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')

        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        message=[]
        if user:
            for record in req.get('products'):
                product = request.env['product.product'].sudo().search(
                    [('id', '=', record['product_id'])])

                if len(product) == 0:
                    # Response.status = '200'
                    # response = {'status': 200, 'message': 'Product Not Found', 'product_id': record['product_id']}
                    # return response
                    value={
                        'message_add_on': '',
                        'add_on_id': 0,
                        'add_on_name': '',
                        'add_on_final_price_Without_TVA': 0.0,
                        'add_on_final_price': 0.0,
                        'message_product': 'Product Not Found',
                        'product_id': record['product_id'],
                        'product_name':'',
                        'final_price_Without_TVA': 0.0,
                        'final_price': 0.0
                    }
                    message.append(value)
                else:

                    if product.app_publish == False:
                        value = {
                            'message_add_on': '',
                            'add_on_id': 0,
                            'add_on_name': '',
                            'add_on_final_price_Without_TVA': 0.0,
                            'add_on_final_price': 0.0,
                            'message_product': 'Product Not Available',
                            'product_id': record['product_id'],
                            'product_name': product.name,
                            'final_price_Without_TVA': 0.0,
                            'final_price': 0.0
                        }
                        message.append(value)

                addons = []
                addons = record['addons_note']
                addon_price = 0
                if addons:
                    addon_price = 0
                    for addon in addons:

                        product_addon = request.env['product.product'].sudo().search(
                            [('id', '=', addon['product_id'])])
                        if len(product_addon) == 0:
                            value = {
                                'message_add_on': 'Add On Not Found',
                                'add_on_id': addon['product_id'],
                                'add_on_name': '',
                                'add_on_final_price_Without_TVA': 0.0,
                                'add_on_final_price': 0.0,
                                'message_product': '',
                                'product_id': record['product_id'],
                                'product_name': product.name,
                                'final_price_Without_TVA': 0,
                                'final_price': 0
                            }
                            message.append(value)


                        else:
                            try:
                                res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                                included = res['total_included']
                                price_product = included
                            except:
                                price_product = product_addon.lst_price

                            price_without_TVA = Product_Info.get_product_product_price(product_addon)
                            if addon['price'] != price_without_TVA:
                                Response.status = '200'

                                values = Product_Info.get_product_product_details(product_addon)

                                value = {
                                    'message_add_on': 'Add On Price Not Correct',
                                    'add_on_id': addon['product_id'],
                                    'add_on_name': product_addon.name,
                                    'add_on_final_price_Without_TVA': values['final_price_Without_TVA'],
                                    'add_on_final_price': values['final_price'],
                                    'message_product': '',
                                    'product_id': record['product_id'],
                                    'product_name': product.name,
                                    'final_price_Without_TVA': 0.0,
                                    'final_price': 0.0

                                }
                                message.append(value)

                            addon_price = addon_price + addon['price']

                price_unit = record['price']

                try:
                    res = product.taxes_id.compute_all(product.lst_price, product=product)
                    included = res['total_included']
                    price_product = included
                except:
                    price_product = product.lst_price


                if round((price_unit - addon_price), 3) != round(Product_Info.get_product_product_price(product), 3):
                    values = Product_Info.get_product_product_details(product)

                    value = {
                        'message_add_on': '',
                        'add_on_id': 0,
                        'add_on_name': '',
                        'add_on_final_price_Without_TVA': 0.0,
                        'add_on_final_price': 0.0,
                        'message_product': 'Price Not Correct',
                        'product_id': product.id,
                        'product_name': product.name,
                        'final_price_Without_TVA': values['final_price_Without_TVA'],
                        'final_price': values['final_price']

                    }
                    message.append(value)

            Response.status = '200'
            response = {'status': 200, 'message': message}
            return response
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
            return response



    @http.route(ProductInfo.version + 'list-user-addresses', type='json', auth='public', methods=['Post'], cors="*")
    def get_list_of_other_address(self):
        req = json.loads(request.httprequest.data)
        # retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        detail = ProductInfo()
        list = []
        if retailer_user:
            if retailer_user.partner_id:

                lat=0
                long=0
                if retailer_user.partner_id.child_ids:
                    try:
                        free_delivery = retailer_user.partner_id.free_delivery
                    except:
                        free_delivery = False

                    for add in retailer_user.partner_id.child_ids:
                        lat= add.partner_latitude if add.partner_latitude else 0
                        long= add.partner_longitude if add.partner_longitude else 0
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
                            'is_default':add.is_default_address if add.is_default_address else False,
                            "can_delete": True,
                            "delivery_info": detail.calcul_for_address(lat, long,None,free_delivery)
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
            
        return response
        
    @http.route(ProductInfo.version + 'add-delivery-address-from-default', type='json', auth='public', methods=['Post'], cors="*")
    def add_delivery_address_from_default(self):
        req = json.loads(request.httprequest.data)

        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        detail = ProductInfo()
        list = []
        if retailer_user:
            if retailer_user.partner_id:
                try:
                    free_delivery = retailer_user.partner_id.free_delivery
                except:
                    free_delivery = False
                lat = retailer_user.partner_id.partner_latitude if retailer_user.partner_id.partner_latitude else 0
                long = retailer_user.partner_id.partner_longitude if retailer_user.partner_id.partner_longitude else 0
                return_calcul = detail.calcul_for_address(lat, long,None,free_delivery)

                if return_calcul:



                    values = {
                        "name": retailer_user.partner_id.name,
                        "mobile": retailer_user.partner_id.mobile if retailer_user.partner_id.mobile else "",
                        "phone": retailer_user.partner_id.phone if retailer_user.partner_id.phone else "",

                        "city": retailer_user.partner_id.city if retailer_user.partner_id.city else "",
                        "street": retailer_user.partner_id.street if retailer_user.partner_id.street else "",
                        "street2": retailer_user.partner_id.street2 if retailer_user.partner_id.street2 else "",
                        "partner_latitude": lat,
                        "partner_longitude": long,
                        "parent_id": retailer_user.partner_id.id,
                        "is_client": True,
                        # "is_member": False,
                        "is_driver": False,
                        "is_manager": False,
                        "type": 'delivery',
                        "zone_id": return_calcul['zone_id'],
                        "is_default_address":True
                    }

                    new_address = request.env['res.partner'].sudo().create(values)

                    try:
                        initial_partner = request.env['res.partner'].sudo().search([('id','=',retailer_user.partner_id.id)])
                        initial_partner.sudo().write(
                            {
                                "zone_id": return_calcul['zone_id']
                            }
                        )
                    except:
                        pass

                    if new_address:
                        Response.status = '201'
                        response = {'status': 201, 'response': new_address.id, 'message': 'new address created'}


                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Default address is out of zones'}


            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'no address found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'user not found'}
        return response
        
    @http.route(ProductInfo.version + 'place-order', type='json', auth='user', methods=['Post'])
    def place_order(self):
        Product_Info = ProductInfo()
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
                        response = {'status': 404, 'message': 'Product Not Found'}
                        return response
                    try:
                        res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                        included = res['total_included']
                        price_product = included
                    except:
                        price_product = product_addon.lst_price

                    if addon['price'] != Product_Info.get_product_product_price(product_addon,price_product):
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Price Not Correct'}
                        return response
                    addon_price = addon_price + addon['price']

            price_unit = record['price']
            try:
                res = product.taxes_id.compute_all(product.lst_price, product=product)
                included = res['total_included']
                price_product = included
            except:
                price_product = product.lst_price
            if price_unit != Product_Info.get_product_product_price(product,price_product):
                Response.status = '404'
                response = {'status': 404, 'message': 'Price Not Correct'}
                return response

        company_id = req.get('company_id')

        boot = request.env['res.users'].sudo().search([('active', '=', False)], order='create_date,id', limit=1)

        user_timezone = boot.tz

        delivery_date_str = req.get('delivery_date')

        date_format = "%d/%m/%Y %H:%M:%S"
        delivery_date = datetime.strptime(delivery_date_str, date_format)

        source_timezone = pytz.timezone('UTC')  # Replace 'UTC' with the actual source timezone

        # Convert the delivery_date from the source timezone to the user_timezone
        # delivery_date = source_timezone.localize(delivery_date).astimezone(pytz.timezone(user_timezone))
        delivery_date = pytz.timezone(user_timezone).localize(delivery_date).astimezone(source_timezone)

        delivery_date_naive = delivery_date.replace(tzinfo=None)

        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        quotation = request.env['sale.order'].sudo().create({
            "partner_id": retailer_user.partner_id.id,
            "state": 'draft',
            "company_id": company_id,
            "delivery_date": delivery_date_naive,
            "sale_order_type": req.get('sale_order_type_id'),
            "partner_shipping_id": req.get('address_id'),
            "user_id":retailer_user
            # "warehouse_id": retailer_user.partner_id.zone_id.warehouse_id.id
        })
        for record in req.get('products'):
            product = request.env['product.product'].sudo().search(
                [('id', '=', record['product_id'])])

            addons = record['addons_note']
            addon_price = 0
            if addons:
                addon_price = 0
                for addon in addons:
                    product_addon = request.env['product.product'].sudo().search(
                        [('id', '=', addon['product_id'])])
                    if product_addon == False:
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Product Not Found'}
                        return response

                    try:
                        res = product_addon.taxes_id.compute_all(product_addon.lst_price, product=product_addon)
                        included = res['total_included']
                        price_product = included
                    except:
                        price_product = product_addon.lst_price

                    if addon['price'] != Product_Info.get_product_product_price(product_addon,price_product):
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Price Not Correct'}
                        return response
                    addon_price = addon_price + addon['price']

            if product:
                request.env['sale.order.line'].sudo().create({
                    "order_id": quotation.id,
                    "product_id": product.id,
                    "product_uom_qty": record['quantity'],
                    'name': product.name,
                    "price_unit": record['price'] + addon_price,
                    # "price_total": record['price_total'],
                    "notes": record['notes'],
                    "addons_note": record['addons_note'],
                    "removable_ingredients_note": record['removable_ingredients_note'],
                    # "price_unit": self.get_promo_price(product.id)
                })
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Product Not Found'}
                return response

        # self.confirm_quot(quotation)
        # notifications_saved = request.env['sent.notification'].sudo().create({
        #     "name": "Your Order has been confirmed!",
        #     "description": "Your order " + str(quotation.name) + " has been confirmed",
        #     "users": [(4, retailer_user.id)],
        #     "order_id": quotation.id,
        #     "notif_type": 'order_confirmed_1'
        # })
        # server_Token = ProductInfo.server_Token
        # device_Token = retailer_user.user_token
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': 'key=' + server_Token,
        # }
        # body = {
        #     'notification': {'title': "Your Order has been confirmed!",
        #                      'body': "Your order " + str(quotation.name) + " has been confirmed",
        #                      },
        #     'to':
        #         device_Token,
        #     'priority': 'high',
        #     "data": {
        #         "sender_id": 3,
        #         "type_id": 11,
        #         "order_id": notifications_saved.order_id.id,
        #         "type_name": dict(notifications_saved._fields['notif_type'].selection).get(
        #             notifications_saved.notif_type),
        #     },
        # }
        #
        # notif = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        Response.status = '200'
        response = {'status': 200, 'message': 'Order Received'}

        return response

    def confirm_quot(self, order):
        order.action_confirm()





    @http.route(ProductInfo.version + 'best-selling-products', type='json', auth='public', methods=['Post'],cors="*")
    def get_best_selling_products(self):
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        request.cr.execute("""
                        select product_template.id,
                        product_template.name, 
                        count(sale_order_line.product_id) as count_of_product 
                        from  sale_order_line  
                        inner join product_product on sale_order_line.product_id = product_product.id
                        inner join product_template on product_product.product_tmpl_id = product_template.id 
                        where sale_order_line.state='sale' and product_template.app_publish=True  
                        group by product_template.id,product_template.name 
                        order by count_of_product Desc
                        """)
        productlists = request.cr.fetchall()
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        # if retailer_user:
        #     all_wishlist = request.env['product.wishlist'].sudo().search(
        #         [('partner_id', '=', retailer_user.partner_id.id)])
        # else:
        #     all_wishlist = False
            
        list = []
        Product_Info = ProductInfo()
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if productlists:
            for product_n in productlists:

                if lang == "ar":
                    product = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                        [('id', '=', product_n[0])])

                else:
                    product = request.env['product.template'].sudo().search([('id', '=', product_n[0])])

                # product = request.env['product.template'].sudo().search(
                #     [('id', '=', product_n[0])])
                is_fav = False
                if retailer_user:
                    all_wishlist = request.env['product.wishlist'].sudo().search(
                        [('partner_id', '=', retailer_user.partner_id.id),
                         ('product_id.product_tmpl_id', '=', product.id)])
                else:
                    all_wishlist = False
                if all_wishlist:
                    is_fav = True
                    # for wish in all_wishlist:
                    #     if product.id == wish.product_template_id.id:
                    #         is_fav = True
                    #         break
                values = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": "/web/content/" + str(
                        product.image_attachment.id) if product.image_attachment.id else "",
                    "price": Product_Info.get_product_template_price(product),
                    # "price": product.list_price,
                    # "retailer_price": self.get_retailer_price(product.id),
                    # "promo_price": self.get_promo_price(product.id),
                    # "product_category_id": product.categ_id.id,
                    # "product_category_name": product.categ_id.name,
                    # 'discount': self.get_retailer_discount(product.id),
                    # "promo_discount": self.get_promo_discount(product.id),
                    # "weight": product.weight,
                    "is_fav": is_fav
                }
                list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of best selling products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

   

    @http.route(ProductInfo.version + 'all-products', type='json', auth='public', methods=['Post'],cors="*")
    def get_list_of_products(self):
        x_localization = request.httprequest.headers.get('x-localization')
        Product_Info = ProductInfo()

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            company_id = False
            pass
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            if company_id:
                products = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service'), ('company_id', 'in', [company_id, False])])
            else:
                products = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service')])

        else:
            if company_id:
                products = request.env['product.template'].sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service'), ('company_id', 'in', [company_id, False])])
            else:
                products = request.env['product.template'].sudo().search(
                    [('app_publish', '=', True), ('type', '!=', 'service')])

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        # if retailer_user:
        #     all_wishlist = request.env['product.wishlist'].sudo().search(
        #         [('partner_id', '=', retailer_user.partner_id.id)])
        # else:
        #     all_wishlist = False
            
        list = []

        if products:
            for product in products:
                is_fav = False
                if retailer_user:
                    all_wishlist = request.env['product.wishlist'].sudo().search(
                        [('partner_id', '=', retailer_user.partner_id.id),
                         ('product_id.product_tmpl_id', '=', product.id)])
                else:
                    all_wishlist = False

                if all_wishlist:
                    is_fav = True
                # if all_wishlist:
                #     for wish in all_wishlist:
                #         if product.id == wish.product_template_id.id:
                #             is_fav = True
                #             break
                the_price = Product_Info.get_product_template_price(product)

                values = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": "/web/content/" + str(product.image_attachment.id) if product.image_attachment.id else "",
                    "price":the_price ,
                    "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id),
                    "category_id": product.categ_id.id,
                    "is_fav": is_fav,
                    "variant_discount": Product_Info.has_variant_discount(product.id,company_id)
                }
                list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

    @http.route(ProductInfo.version + 'all-products-public', type='json', auth='public', methods=['Post'],cors="*")
    def get_list_of_products_public(self):
        products = request.env['product.template'].sudo().search([('detailed_type', '=', 'product')])
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        # if retailer_user:
        #     all_wishlist = request.env['product.wishlist'].sudo().search(
        #         [('partner_id', '=', retailer_user.partner_id.id)])
        # else:
        #     all_wishlist = False
            
        list = []
        Product_Info = ProductInfo()
        if products:
            for product in products:
                is_fav = False
                if retailer_user:
                    all_wishlist = request.env['product.wishlist'].sudo().search(
                        [('partner_id', '=', retailer_user.partner_id.id),
                         ('product_id.product_tmpl_id', '=', product.id)])
                else:
                    all_wishlist = False

                if all_wishlist:
                    is_fav = True
                # if all_wishlist:
                #     for wish in all_wishlist:
                #         if product.id == wish.product_template_id.id:
                #             is_fav = True
                #             break
                values = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": "/web/content/" + str(product.image_attachment.id) if product.image_attachment.id else "",
                    "price": Product_Info.get_product_template_price(product),
                    # "price": product.list_price,
                    # "retailer_price": self.get_retailer_price(product.id),
                    # "promo_price": self.get_promo_price(product.id),
                    # "product_category_id": product.categ_id.id,
                    # "product_category_name": product.categ_id.name,
                    # 'discount': self.get_retailer_discount(product.id),
                    # "promo_discount": self.get_promo_discount(product.id),
                    # "weight": product.weight,
                    "is_fav": is_fav
                }
                list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

    @http.route(ProductInfo.version + 'latest-dollar-rate-public', type='json', auth='public', methods=['Post'],cors="*")
    def get_daily_dollar_rate_public(self):
        usd_currency = request.env['res.currency'].sudo().search([('name', '=', 'LBP')])
        if usd_currency:
            usd_latest_rate = request.env['res.currency.rate'].sudo().search([('currency_id', '=', usd_currency.id)],
                                                                             order='name desc', limit=1).company_rate
            val = {"last_rate": usd_latest_rate}
            Response.status = '200'
            response = {'status': 200, 'response': val, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Rate found!'}
        return response

    @http.route(ProductInfo.version + 'all-products-public-http', type='json', auth="public", cors='*', methods=['POST'])
    def get_list_of_products_public_http(self):
        products = request.env['product.template'].sudo().search([('detailed_type', '=', 'product')])
        list = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        Product_Info = ProductInfo()
        if products:
            for product in products:
                values = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_image": str(base_url) + "/web/content/" + str(product.image_attachment.id) if product.image_attachment.id else "",
                    "price": Product_Info.get_product_template_price(product),
                    # "price": product.list_price,
                    "product_category_id": product.categ_id.id,
                    "product_category_name": product.categ_id.name,
                    "weight": product.weight,
                }
                list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

    @http.route(ProductInfo.version + 'set-address-as-default', type='json', auth='public', methods=['Post'], cors="*")
    def set_address_as_default(self):
        req = json.loads(request.httprequest.data)

        retailer_user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        partner_id = req.get('address_id')
        if partner_id:
            partner = request.env['res.partner'].sudo().search([('id', '=',partner_id)])
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Address not found'}
            return response

        detail = ProductInfo()
        list = []
        if retailer_user:
            if retailer_user.partner_id:


                if retailer_user.partner_id.child_ids:

                    if partner in retailer_user.partner_id.child_ids:
                        for add in retailer_user.partner_id.child_ids:
                            add.sudo().write({
                                'is_default_address': False
                            })
                            if add.id == partner_id:
                                add.sudo().write({
                                    'is_default_address' : True
                                })


                        Response.status = '200'
                        response = {'status': 200,  'message': 'Default Address is Set'}
                    else:
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Address not found'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'no other address found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response


    def products_name_translate_old(self):
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        products_result_list =[]
        products_list = req.get('products')
        company_id = req.get('company_id')
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"


        if products_list:
            for product in products_list:
                product_id = product['product_id']


                thename = Product_Info.get_the_full_product_product_name(product_id,lang)
                val = {
                    "product_id":product_id,
                    "name":thename if thename else ""
                }
                addons_note_list = []
                if "addons_note" in product:

                    for addon_id in product['addons_note']:

                        thename = Product_Info.get_the_full_product_product_name(addon_id, lang)
                        value_add_on={
                            "product_id": addon_id,
                            "name": thename if thename else ""
                        }
                        addons_note_list.append(value_add_on)
                val['addons_note'] = addons_note_list

                removable_ingredients_note_list = []
                if "removable_ingredients_note" in product:

                    for removable_ingredient_id in product['removable_ingredients_note']:

                        thename = Product_Info.get_the_full_product_product_name(removable_ingredient_id, lang)
                        value_removable_ingredient = {
                            "product_id": removable_ingredient_id,
                            "name": thename if thename else ""
                        }
                        removable_ingredients_note_list.append(value_removable_ingredient)
                val['removable_ingredients_note'] = removable_ingredients_note_list

                combo_content_list = []
                if "combo_content" in product:

                    for combo_content_id in product['combo_content']:
                        attribute_value_name = ''
                        if lang == 'ar':
                            attribute_value = request.env['product.attribute.value'].with_context(
                                lang='ar_001').sudo().search(
                                [('id', '=', combo_content_id['value_value_id'])])
                        else:
                            attribute_value = request.env['product.attribute.value'].sudo().search(
                                [('id', '=', combo_content_id['value_value_id'])])

                        thename = Product_Info.get_the_full_product_product_name(combo_content_id['product_id'], lang) + '(' + attribute_value.name + ')'
                        combo_content_ingredient = {
                            "product_id": combo_content_id,
                            "name": thename if thename else ""
                        }
                        combo_content_list.append(combo_content_ingredient)
                val['combo_content'] = combo_content_list

                products_result_list.append(val)

            Response.status = '200'
            response = {'status': 200,'response':products_result_list,'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'list of products not found'}

        return response

    @http.route(ProductInfo.version + 'products-name-translate', type='json', auth='public', methods=['Post'], cors="*")
    def products_name_translate(self):
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        products_result_list =[]
        products_list = req.get('products')
        company_id = req.get('company_id')
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"


        if products_list:
            for product in products_list:
                product_id = product['product_id']


                thename = Product_Info.get_the_full_product_product_name(product_id,lang)
                val = {
                    "product_id":product_id,
                    "name":thename if thename else ""
                }
                parents_list=[]
                if "parents" in product:
                    for parent in product['parents']:
                        product_id = parent['product_id']
                        thename = Product_Info.get_the_full_product_product_name(product_id, lang)
                        value_parent = {
                            "product_id": product_id,
                            "name": thename if thename else ""
                        }
                        parents_list.append(value_parent)
                val['parents'] = parents_list

                addons_note_list = []
                if "addons_note" in product:

                    for addon in product['addons_note']:
                        addon_id = addon['product_id']
                        thename = Product_Info.get_the_full_product_product_name(addon_id, lang)
                        value_add_on={
                            "parent_id": addon['parent_id'],
                            "product_id": addon_id,
                            "name": thename if thename else ""
                        }
                        addons_note_list.append(value_add_on)
                val['addons_note'] = addons_note_list

                removable_ingredients_note_list = []
                if "removable_ingredients_note" in product:

                    for removable_ingredient in product['removable_ingredients_note']:
                        removable_ingredient_id = removable_ingredient['product_id']
                        thename = Product_Info.get_the_full_product_product_name(removable_ingredient_id, lang)
                        value_removable_ingredient = {
                            "parent_id": removable_ingredient['parent_id'],
                            "product_id": removable_ingredient_id,
                            "name": thename if thename else ""
                        }
                        removable_ingredients_note_list.append(value_removable_ingredient)
                val['removable_ingredients_note'] = removable_ingredients_note_list

                combo_content_list = []
                if "combo_content" in product:

                    for combo_content in product['combo_content']:
                        attribute_value_name = ''
                        if lang == 'ar':
                            attribute_value = request.env['product.attribute.value'].with_context(
                                lang='ar_001').sudo().search(
                                [('id', '=', combo_content['value_value_id'])])
                        else:
                            attribute_value = request.env['product.attribute.value'].sudo().search(
                                [('id', '=', combo_content['value_value_id'])])

                        thename = Product_Info.get_the_full_product_product_name(combo_content['product_id'], lang) + '(' + attribute_value.name + ')'
                        combo_content_ingredient = {
                            "value_value_id": combo_content['value_value_id'],
                            "product_id": combo_content['product_id'],
                            "name": thename if thename else ""
                        }
                        combo_content_list.append(combo_content_ingredient)
                val['combo_content'] = combo_content_list

                products_result_list.append(val)

            Response.status = '200'
            response = {'status': 200,'response':products_result_list,'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'list of products not found'}

        return response
