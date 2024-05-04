from odoo.http import request
from odoo.http import Response
import json
from odoo import http
from odoo.addons.das_publicfunction.controller.main import ProductInfo
# from slugify import slugify
import re

class MainPageSection(http.Controller):
    @http.route('/api/main-page-section', type='json', auth="public", cors='*', methods=['POST'])
    def get_main_page_section(self):
        req = json.loads(request.httprequest.data)
        section_number = req.get('number')
        try:
            company_id = req.get('company_id')
        except:
            pass
        if section_number:
            x_localization = request.httprequest.headers.get('x-localization')
            lang = "en"
            if x_localization:
                if x_localization == 'ar':
                    lang = "ar"

            if lang == "ar":
                if company_id:
                    section = request.env['main.page.section'].with_context(lang='ar_001').sudo().search(
                        [('section_number', '=', str(section_number)),('company_id','=',company_id)], limit=1)
                else:
                    section = request.env['main.page.section'].with_context(lang='ar_001').sudo().search(
                        [('section_number', '=', str(section_number))], limit=1)

            else:
                if company_id:
                    section = request.env['main.page.section'].sudo().search(
                        [('section_number', '=', str(section_number)),('company_id','=',company_id)], limit=1)
                else:
                    section = request.env['main.page.section'].sudo().search(
                        [('section_number', '=', str(section_number))], limit=1)


            if section:

                ads_list = []
                product_list = []
                
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

                # query = 'Select product_template_id From main_page_section_product_template_rel where main_page_section_id=' + str(
                #     section.id)
                # request.env.cr.execute(query)
                # res = request.env.cr.fetchall()

                for product in section.product_ids:
                    is_fav = False
                    if all_wishlist:
                        for wish in all_wishlist:
                            if product.id == wish.product_template_id.id:
                                is_fav = True
                                break
                    if lang == "ar":
                        thetemplate = request.env['product.template'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', product.id)])
                    else:
                        thetemplate = request.env['product.template'].sudo().search(
                            [('id', '=', product.id)])
                    # if thetemplate.description :
                    #     desc = re.sub(r'<.*?>', ' ', thetemplate.description)
                    # else:
                    #     desc = ''
                    # desc = desc.strip()
                    if product.app_publish == True:

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
                        product_list.append({"product_id": product.id,
                                             "product_name": thetemplate.name,
                                             "product_description": Product_Info.change_parag_to_line(
                                                 thetemplate.description_sale),
                                             "product_image": "/web/content/" + str(
                                                 product.image_attachment.id) if product.image_attachment.id else "",
                                             # "price": product.list_price,
                                             "price": the_price,
                                             "price_list": Product_Info.get_prices_for_currency_list(the_price,
                                                                                                     company_id),
                                             'template_sale_price_new': new_price,
                                             'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                                                 new_price, company_id),
                                             'template_sale_price_old': round(price_product, 2),
                                             'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                                                 price_product, company_id),
                                             'percent_discount': percent_discount,
                                             'is_fav': is_fav,
                                             "category_id": product.categ_id.id,
                                             "variant_discount": Product_Info.has_variant_discount(product.id,
                                                                                                   company_id)
                                             })

                vals = {
                    "id": section.id,
                    "name": section.name if section.name else "",
                    # "slug_name": slugify(section.name) if section.name else "",
                    "image": "/web/content/" + str(
                        section.main_page_section_image_attachment.id) if section.main_page_section_image_attachment.id else "",
                    "product_ids": product_list,
                }

                Response.status = '200'
                response = {'status': 200, 'response': vals, 'message': 'List Of main page section Found'}
            else:

                # product_list = []
                # vals = {
                #     "id": 0,
                #     "name":  "",
                #     "image": "",
                #     "product_ids": product_list,
                # }
                Response.status = '404'
                # response = {'status': 404,'response': vals, 'message': 'No section Found'}
                response = {'status': 404, 'message': 'No section Found'}
        else:
            # product_list = []
            # vals = {
            #     "id": 0,
            #     "name": "",
            #     "image": "",
            #     "product_ids": product_list,
            # }
            Response.status = '404'
            # response = {'status': 200, 'response': vals, 'message': 'No section Found'}
            response = {'status': 200,  'message': 'No section Found'}
        return response

