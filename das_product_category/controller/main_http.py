import json
from odoo.http import Response
from odoo import http
from odoo.http import request
import json
from datetime import date, datetime


from odoo.addons.das_publicfunction.controller.main import ProductInfo

class ProductCategoryHttp(http.Controller):
    @http.route('/api/all-category-post-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_all_category(self):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            company_id = request.params.get('company_id')
        except:
            company_id = -1
        x_localization = request.httprequest.headers.get('x-localization')
        all = []
        if company_id!=-1 and company_id!=None:

            all_category = request.env['product.category'].sudo().search(
                [('is_publish', '=', True), ('company_id', '=', int(company_id))])

        else:

            all_category = request.env['product.category'].sudo().search([('is_publish', '=', True)])

        if all_category:
            for cat in all_category:
                catname = cat.name
                if x_localization:
                    if x_localization == 'ar':
                        catname = str(cat.name_ar) if cat.name_ar else ""

                create_datetime = cat.create_date.strftime('%Y-%m-%d %H:%M:%S')
                write_datetime = cat.write_date.strftime('%Y-%m-%d %H:%M:%S')
                all.append({'id': cat.id,
                            "name": catname,
                            "company_id": cat.company_id.id,
                            "parent_id": cat.parent_id.id if cat.parent_id.id else -1,
                            "position": 0,
                            "status": 1,
                            "created_at": create_datetime,
                            "updated_at": write_datetime,
                            "image": base_url + "/web/content/" + str(cat.image_attachment.id) if cat.image_attachment.id else "",
                            "banner_image": base_url + "/web/content/" + str(
                                cat.image_attachment.id) if cat.image_attachment.id else "",
                            "slug": "",  # slugify(cat.name),
                            "sorting": 0,

                            }
                           )

            Response.status = '200'
            response = {'status': 200, 'response': all, 'message': 'List Of Categories Found'}
        else:
            Response.status = '200'
            response = {'status': 200,'response':[], 'message': 'No data Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route('/api/category_product-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_all_category_products(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            thecategory_id = int(request.params.get('category_id'))
        except:
            thecategory_id = -1

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        category_id = request.env['product.category'].sudo().search(
            [('id', '=', thecategory_id)])

        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = False
        # if category_id.company_id:
        #     company_id = category_id.company_id.id
        # else:
        #     company_id = False
        if user_id!=-1:
            retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        else:
            retailer_user = False

        if retailer_user:
            all_wishlist = request.env['product.wishlist'].sudo().search(
                [('partner_id', '=', retailer_user.partner_id.id)])
        else:
            all_wishlist = False
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
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
                        [('categ_id', '=', category_id.id),('app_publish', '=', True)])

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
                                         "product_image": base_url + "/web/content/" + str(product.image_attachment.id) if product.image_attachment else "",
                                         "price": the_price,
                                         "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id),
                                         'template_sale_price_new': new_price,
                                         'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                                             new_price,company_id),
                                         'template_sale_price_old': round(price_product, 2),
                                         'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                                             price_product,company_id),
                                         'percent_discount': percent_discount,
                                         "is_fav": is_fav,
                                         "variant_discount": Product_Info.has_variant_discount(product.id, company_id)
                                         })

            Response.status = '200'
            response = {'status': 200, 'response': product_list, 'message': 'List Of Product Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
