import json
from odoo.http import Response
from odoo import http
from odoo.http import request
import json
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class Product(http.Controller):
    @http.route('/api/search-product', type='json', auth='public', methods=['Post'], cors="*")
    def search_product(self):
        req = json.loads(request.httprequest.data)

        try:

            company_id = req.get('company_id')
        except:
            company_id = False


        # try:
        #     product_name = req.get('product_name')
        #     if product_name == '':
        #         product_name = False
        # except:
        #     product_name = False

        # if product_name == False or   product_name == None:
        #     Response.status = '200'
        #     response = {'status': 200, 'message': 'You must enter product name'}
        #     return response


        if company_id:
            products = request.env['product.template'].sudo().search(
                [('company_id', 'in', [company_id,False]),('name', 'ilike', req.get('product_name')), ('app_publish', '=', True)])

            products_ar = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                [('company_id', 'in', [company_id,False]),('name', 'ilike', req.get('product_name')), ('app_publish', '=', True)])
        else:
            products = request.env['product.template'].sudo().search(
                [('name', 'ilike', req.get('product_name')), ('app_publish', '=', True)])
            products_ar = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                [('name', 'ilike', req.get('product_name')), ('app_publish', '=', True)])


        user_id = req.get('user_id')
        if user_id:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        if retailer_user:
            all_wishlist = request.env['product.wishlist'].sudo().search(
                [('partner_id', '=', retailer_user.partner_id.id)])
        else:
            all_wishlist = False
            
        list = []
        Product_Info = ProductInfo()
        if products:
            for product in products:
                is_fav = False
                if all_wishlist:
                    for wish in all_wishlist:
                        if product.id == wish.product_template_id.id:
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
                    "product_image": "/web/content/" + str(
                        product.image_attachment.id) if product.image_attachment.id else "",
                    "price": the_price,
                    "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id),
                    'template_sale_price_new': new_price,
                    'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(new_price,company_id),
                    'template_sale_price_old': round(price_product, 2),
                    'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(price_product ,company_id),
                    'percent_discount': percent_discount,
                    "is_fav": is_fav,
                    "category_id": product.categ_id.id,
                    "variant_discount": Product_Info.has_variant_discount(product.id,  company_id)
                }
                list.append(values)

        if products_ar:
            for product in products_ar:
                if product in products:
                    pass
                else:
                    is_fav = False
                    if all_wishlist:
                        for wish in all_wishlist:
                            if product.id == wish.product_template_id.id:
                                is_fav = True
                    the_price = Product_Info.get_product_template_price(product)
                    values = {
                        "product_id": product.id,
                        "product_name": product.name,
                        "product_image": "/web/content/" + str(
                            product.image_attachment.id) if product.image_attachment.id else "",
                        "price": the_price ,
                        "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id) ,
                        "is_fav": is_fav,
                        "category_id": product.categ_id.id
                    }
                    list.append(values)
        if list:
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

    

    @http.route('/api/all-products-public-http', type='json', auth="public", cors='*', methods=['POST'])
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
                    "product_image": str(base_url) + "/web/content/" + str(product.image_attachment.id),
                    # "price": product.list_price,
                    "price": Product_Info.get_product_template_price(product),
                    "product_category_id": product.categ_id.id,
                    "product_category_name": product.categ_id.name,
                    # "weight": product.weight,
                }
                list.append(values)
            Response.status =   '200'
            response = {'status': 200, 'response': list, 'message': 'list of products'}
        else:
            Response.status =   '404'
            response = {'status': 404, 'message': 'no products found'}
        return response

