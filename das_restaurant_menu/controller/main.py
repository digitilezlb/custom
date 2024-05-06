import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import json
from  odoo.addons.das_publicfunction.controller.main import ProductInfo


class RestaurantMenu(http.Controller):
    @http.route('/api/website-menu', type='json', auth='public', methods=['Post'], cors="*")
    def get_website_menu(self):
        req = json.loads(request.httprequest.data)

        try:
            company_id = req.get('company_id')
        except:
            company_id = False

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            if company_id:
                menu = request.env['das.menu'].with_context(lang='ar_001').sudo().search(
                    [('is_web_menu','=',True),('company_id', 'in', [company_id, False])], limit=1)
            else:
                menu = request.env['das.menu'].with_context(lang='ar_001').sudo().search(
                    [('is_web_menu','=',True)], limit=1)

        else:
            if company_id:
                menu = request.env['das.menu'].sudo().search(
                    [('is_web_menu','=',True),('company_id', 'in', [company_id, False])], limit=1)

            else:
                menu = request.env['das.menu'].sudo().search(
                    [('is_web_menu','=',True)], limit=1)

        if menu:
            category_list = []

            for cat in menu.categories:

                if lang == "ar":
                    category = request.env['das.category.menu'].with_context(
                        lang='ar_001').sudo().search(
                        [('id', '=', cat.id)])
                else:
                    category = request.env['das.category.menu'].sudo().search(
                        [('id', '=', cat.id)])

                parent_id = category.parent_id
                cat_value ={
                    "category_name":category.name,
                    "category_image":"/web/content/" + str(
                            category.category_menu_image_attachment.id) if category.category_menu_image_attachment.id else "",
                    "products":self.get_category_products(category)
                }
                category_list.append(cat_value)
            value ={
                "name":menu.name,
                "type":menu.type_id.name,
                "qr_code":menu.qr_code,
                "image": "/web/content/" + str(
                    menu.menu_image_attachment.id) if menu.menu_image_attachment.id else "",
                "categories":category_list

            }
            Response.status = '200'
            response = {'status': 200, 'response': value,  'message': 'Menu Found'}
        else:

            Response.status = '404'
            response = {'status': 404, 'message': 'No Menu Found'}
        
        return response

    @http.route('/api/website-menu-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_website_menu(self):


        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        # try:
        #     day_of_week = request.params.get('day_of_week')
        # except:
        #     day_of_week = -1

        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = False


        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            if company_id:
                menu = request.env['das.menu'].with_context(lang='ar_001').sudo().search(
                    [('is_web_menu', '=', True), ('company_id', 'in', [company_id, False])], limit=1)
            else:
                menu = request.env['das.menu'].with_context(lang='ar_001').sudo().search(
                    [('is_web_menu', '=', True)], limit=1)

        else:
            if company_id:
                menu = request.env['das.menu'].sudo().search(
                    [('is_web_menu', '=', True), ('company_id', 'in', [company_id, False])], limit=1)

            else:
                menu = request.env['das.menu'].sudo().search(
                    [('is_web_menu', '=', True)], limit=1)

        if menu:
            category_list = []

            for cat in menu.categories:

                if lang == "ar":
                    category = request.env['das.category.menu'].with_context(
                        lang='ar_001').sudo().search(
                        [('id', '=', cat.id)])
                else:
                    category = request.env['das.category.menu'].sudo().search(
                        [('id', '=', cat.id)])

                parent_id = category.parent_id
                cat_value = {
                    "category_name": category.name,
                    "category_image": base_url + "/web/content/" + str(
                        category.category_menu_image_attachment.id) if category.category_menu_image_attachment.id else "",
                    "products": self.get_category_products(category)
                }
                category_list.append(cat_value)
            value = {
                "name": menu.name,
                "type": menu.type_id.name,
                "qr_code": menu.qr_code,
                "image": base_url + "/web/content/" + str(
                    menu.menu_image_attachment.id) if menu.menu_image_attachment.id else "",
                "categories": category_list

            }
            Response.status = '200'
            response = {'status': 200, 'response': value, 'message': 'Menu Found'}
        else:

            Response.status = '404'
            response = {'status': 404, 'message': 'No Menu Found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
    def get_category_products(self,category):
        products = category.product_ids
        Product_Info = ProductInfo()
        product_list =[]
        for product in products:
            if product.app_publish == True:

                product_list.append(Product_Info.get_product_product_details(product,'', 0))
        return product_list