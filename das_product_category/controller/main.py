import json
from odoo.http import Response
from odoo import http
from odoo.http import request
import json
from datetime import date, datetime
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class ProductCategory(http.Controller):
    
    @http.route('/api/all-category-post-user', type='json', auth='user', methods=['Post'],cors='*' )
    def get_all_category_user(self ):
        x_localization = request.httprequest.headers.get('x-localization')
        all = []
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass

        if company_id:
            all_category = request.env['product.category'].sudo().search(
                [('is_publish', '=', True), ('company_id', '=', company_id)])
        else:
            all_category = request.env['product.category'].sudo().search([('is_publish', '=', True)])

        if all_category:
            for cat in all_category:
                catname = cat.name
                if x_localization:
                    if x_localization == 'ar':
                        catname = str(cat.name_ar) if cat.name_ar else ""

                all.append({'id': cat.id,
                            "name": catname,
                            "company_id": cat.company_id.id,
                            "parent_id": cat.parent_id.id if cat.parent_id.id else -1,
                            "position": 0,
                            "status": 1,
                            "created_at": cat.create_date,
                            "updated_at": cat.write_date,
                            "image": "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment.id else "",
                            "banner_image": "/web/content/" + str(
                                cat.image_attachment.id) if cat.image_attachment.id else "",
                            "slug": "",
                            "sorting": 0,

                            }
                           )

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response
        
    # get the grocery category
    @http.route('/api/grocery-category', type='json', auth='public', methods=['Post'], cors="*")
    def get_grocery_category(self):
        grocery_category = request.env['product.category'].sudo().search([('is_grocery', '=', True)])
        if grocery_category:
            sub_cat = []
            grocery_sub_category = request.env['product.category'].sudo().search(
                [('parent_id', '=', grocery_category.id)])
            for cat in grocery_sub_category:
                val = {
                    "id": cat.id,
                    "name": cat.name,
                    "name_ar": cat.name_ar,
                    "image": "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment else ""
                }
                sub_cat.append(val)
            information = []
            information.append({'category_id': grocery_category.id,
                                'category_name': grocery_category.name,
                                'category_name_ar': grocery_category.name_ar,
                                'category_image': "/web/content/" + str(grocery_category.image_attachment.id),
                                'sub_categories': sub_cat})
            Response.status = '200'
            response = {'status': 200, 'response': information, 'message': 'List Of Grocery Sub Category Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    # create 201
    # products bundles
    @http.route('/api/bundle-product', type='json', auth='public', methods=['Post'], cors="*")
    def get_bundle_products(self):
        bundles_products = request.env['product.template'].sudo().search(
            [('is_bundle', '=', True), ('app_publish', '=', True)])
        Product_Info = ProductInfo()
        if bundles_products:
            information = []
            for bundle in bundles_products:
                bundle_bom = request.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', bundle.id)])
                bundle_product_information = []
                for line in bundle_bom.bom_line_ids:
                    try:
                        if line.product_id.product_template_variant_value_ids:
                            product_variant_name = line.product_id.product_template_variant_value_ids  # .product_attribute_value_id.attribute_id.name + ':' + line.product_id.product_template_variant_value_ids.product_attribute_value_id.name
                        else:
                            product_variant_name = ''
                    except:
                        product_variant_name = ''

                    bundle_product_information.append({
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                        'product_product_id': line.product_id.id,
                        'product_name': line.product_id.product_tmpl_id.name,
                        'product_variant_name': product_variant_name,
                        'quantity': int(line.product_qty),
                    })
                information.append({'bundle_id': bundle.id,
                                    'bundle_name': bundle.name,
                                    'bundle_price': Product_Info.get_product_template_price(bundle),
                                    # 'bundle_price': bundle.list_price,
                                    'bundle_image': "/web/content/" + str(bundle.image_attachment.id),
                                    'products': bundle_product_information})
            Response.status = '200'
            response = {'status': 200, 'response': information, 'message': 'List Of Bundles Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    # get the new arrivals
    @http.route('/api/new-arrivals', type='json', auth='public', methods=['Post'], cors="*")
    def get_new_arrivals_arrivals_products_list(self):
        products = []
        new_arrivals_products = request.env['product.template'].sudo().search(
            [('website_ribbon_id', '=', request.env.ref('website_sale.new_ribbon').id), ('app_publish', '=', True)])
        
        req = json.loads(request.httprequest.data)
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
            
        Product_Info = ProductInfo()
        if new_arrivals_products:
            for product in new_arrivals_products:
                is_fav = False
                if all_wishlist:
                    for wish in all_wishlist:
                        if product.id == wish.product_template_id.id:
                            is_fav = True
                            break
                values = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'is_fav': is_fav,
                    'product_image': "/web/content/" + str(product.image_attachment.id),
                    'price':  Product_Info.get_product_template_price(product) ,
                    # 'price': product.list_price,
                }
                products.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': products, 'message': 'List Of New arrivals Products Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response



    # all categories
    @http.route('/api/all-category', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_category_old(self):
        all_category = request.env['product.category'].sudo().search([('is_publish','=',True)])

        # x_localization = request.httprequest.headers.get('x-localization')
        all = []

        if all_category:
            for cat in all_category:
                catname = cat.name
                # if x_localization:
                #     if x_localization == 'ar':
                #         catname = str(cat.name_ar) if cat.name_ar else ""

                all.append({'id': cat.id,
                            "name": catname,
                            "parent_id": cat.parent_id.id if cat.parent_id.id else -1,
                            "position": 0,
                            "status": 1,
                            "created_at": cat.create_date,
                            "updated_at": cat.write_date,
                            "image": "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment.id else "",
                            "banner_image": "/web/content/" + str(
                                cat.image_attachment.id) if cat.image_attachment.id else "",
                            "slug": "",
                            "sorting": 0,

                            }
                           )

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/all-category-post', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_category(self):
        # all_category = request.env['product.category'].sudo().search([('is_publish','=',True)])

        x_localization = request.httprequest.headers.get('x-localization')
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass
        all = []
        if company_id:
            all_category = request.env['product.category'].sudo().search([('is_publish', '=', True),('company_id', '=', company_id)])
        else:
            all_category = request.env['product.category'].sudo().search([('is_publish', '=', True)])
        if all_category:
            for cat in all_category:
                catname = cat.name
                if x_localization:
                    if x_localization == 'ar':
                        catname = str(cat.name_ar) if cat.name_ar else ""

                all.append({'id': cat.id,
                            "name": catname,
                            "company_id": cat.company_id.id,
                            "parent_id": cat.parent_id.id if cat.parent_id.id else -1,
                            "position": 0,
                            "status": 1,
                            "created_at": cat.create_date,
                            "updated_at": cat.write_date,
                            "image": "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment.id else "",
                            "banner_image": "/web/content/" + str(
                                cat.image_attachment.id) if cat.image_attachment.id else "",
                            "slug": "",
                            "sorting": 0,

                            }
                           )

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/all-category-public', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_category_public(self):
        all_category = request.env['product.category'].sudo().search([])
        all = []
        if all_category:
            for cat in all_category:
                all.append({'category_id': cat.id,
                            "category_name": cat.name,
                            "category_name_ar": cat.name_ar,
                            "category_image": "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment else ""})

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    # get all the product for specific category
    @http.route('/api/category_product', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_category_products(self):
        req = json.loads(request.httprequest.data)
        category_id = request.env['product.category'].sudo().search(
            [('id', '=', req.get('category_id'))])
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

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
        company_id =  req.get('company_id')
        # if category_id.company_id:
        #     company_id = category_id.company_id.id
        # else:
        #     company_id = False

        product_list = []
        Product_Info = ProductInfo()
        if category_id:
            if lang == "ar":
                if company_id:
                    product_ids = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                        [('company_id','in',[company_id,False]),('categ_id', '=', category_id.id), ('app_publish', '=', True)])
                else:
                    product_ids = request.env['product.template'].with_context(lang='ar_001').sudo().search(
                        [('categ_id', '=', category_id.id), ('app_publish', '=', True)])
            else:
                if company_id:
                    product_ids = request.env['product.template'].sudo().search(
                        [('company_id','in',[company_id,False]),('categ_id', '=', category_id.id), ('app_publish', '=', True)])
                else:
                    product_ids = request.env['product.template'].sudo().search(
                        [('categ_id', '=', category_id.id), ('app_publish', '=', True)])

            if product_ids:
                for product in product_ids:
                    is_fav = False
                    if all_wishlist:
                        for wish in all_wishlist:
                            if product.id == wish.product_template_id.id:
                                is_fav = True
                                break
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
                    product_list.append({'product_id': product.id,
                                         "product_name": product.name,
                                         "product_image": "/web/content/" + str(product.image_attachment.id) if product.image_attachment else "",
                                         "price": the_price ,
                                         "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id)  ,
                                         'template_sale_price_new': new_price,
                                         'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(new_price,company_id),
                                         'template_sale_price_old': round(price_product, 2),
                                         'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(price_product,company_id ),
                                         'percent_discount': percent_discount,
                                         "is_fav": is_fav,
                                         "variant_discount": Product_Info.has_variant_discount(product.id, company_id)
                                         })

            Response.status = '200'
            response = {'status': 200, 'response': product_list, 'message': 'List Of Product Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    # get the new arrivals list
    @http.route('/api/new-arrivals-list', type='json', auth='public', methods=['Post'], cors="*")
    def get_new_arrivals_products_list(self):
        products = []
        new_arrivals_products = request.env['product.template'].sudo().search(
            [('website_ribbon_id', '=', request.env.ref('website_sale.new_ribbon').id), ('app_publish', '=', True)])
        retailer_user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        all_wishlist = request.env['product.wishlist'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id)])
        Product_Info = ProductInfo()
        if new_arrivals_products:
            for product in new_arrivals_products:
                is_fav = False
                for wish in all_wishlist:
                    if product.id == wish.product_template_id.id:
                        is_fav = True
                values = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'is_fav': is_fav,
                    'product_image': "/web/content/" + str(product.image_attachment.id) if product.image_attachment else "",
                    'price':  Product_Info.get_product_template_price(product) ,
                    # 'price': product.list_price,
                }
                products.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': products, 'message': 'List Of New arrivals Products Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/all-category-public-http', type='json', auth="public", cors='*', methods=['POST'])
    def get_all_category_public_http(self):
        all_category = request.env['product.category'].sudo().search(
            ['|', ('is_grocery', '=', True), ('is_main', '=', True)])
        all = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        if all_category:
            for cat in all_category:
                sub_category_list = []
                for sub in cat.child_id:
                    sub_category_list.append({
                        "sub_category_id": sub.id,
                        "sub_category_name": sub.name
                    })
                all.append({'category_id': cat.id,
                            "category_name": cat.name,
                            "category_image": str(base_url) + "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment else "",
                            "sub_categories": sub_category_list
                            })

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/category-product-http', type='json', auth="public", cors='*', methods=['POSt'])
    def get_all_category_products_http(self):
        req = json.loads(request.httprequest.data)
        category_id = request.env['product.category'].sudo().search(
            [('id', '=', req.get('category_id'))])
        product_list = []
        Product_Info = ProductInfo()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        if category_id:
            product_ids = request.env['product.template'].sudo().search(
                [('categ_id', '=', category_id.id)])
            if product_ids:
                for product in product_ids:
                    product_list.append({'product_id': product.id,
                                         "product_name": product.name,
                                         "product_image": str(base_url) + "/web/content/" + str(
                                             product.image_attachment.id),
                                         "price":  Product_Info.get_product_template_price(product)
                                         # "price": product.list_price
                                         })
            Response.status = '200'
            response = {'status': 200, 'response': product_list, 'message': 'List Of Product Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/product-details-http', type='json', auth="public", cors='*', methods=['POST'])
    def get_product_details(self):
        req = json.loads(request.httprequest.data)
        product_id = request.env['product.template'].sudo().search(
            [('id', '=', req.get('product_id'))])
        product_list = []
        cross_products = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        Product_Info = ProductInfo()
        if product_id:
            product_ids = request.env['product.template'].sudo().search(
                [('categ_id', '=', product_id.categ_id.id)], limit=4)
            for product in product_ids:
                product_list.append({'product_id': product.id,
                                     "product_name": product.name,
                                     "product_image": str(base_url) + "/web/content/" + str(
                                         product.image_attachment.id),
                                     "price": Product_Info.get_product_template_price(product)
                                     # "price": product.list_price
                                     })
            for cross in product_id.accessory_product_ids:
                cross_products.append(
                    {
                        "product_id": cross.product_tmpl_id.id,
                        "product_name": cross.product_tmpl_id.name,
                        "product_image": str(base_url) + "/web/content/" + str(
                            cross.product_tmpl_id.image_attachment.id),
                        "price": Product_Info.get_product_template_price(cross.product_tmpl_id)
                        # "price": cross.product_tmpl_id.list_price
                    }
                )
            images = request.env['product.image'].sudo().search([('product_tmpl_id', '=', product_id.id)])
            images_list = []
            for image in images:
                images_list.append(str(base_url) + "/web/content/" + str(image.image_attachment.id))
            vals = {'product_id': product_id.id,
                    "product_name": product_id.name,
                    "product_image": str(base_url) + "/web/content/" + str(product_id.image_attachment.id),
                    "price": Product_Info.get_product_template_price(product_id),
                    # "price": product_id.list_price,
                    "description": Product_Info.change_parag_to_line(product_id.description_sale),
                    "product_category_id": product_id.categ_id.id,
                    "product_category_name": product_id.categ_id.name,
                    "same_category_product": product_list,
                    "cross_products": cross_products[-4:],
                    "images": images_list
                    }
            Response.status = '200'
            response = {'status': 200, 'response': vals, 'message': 'Product Information Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response
