import json
from odoo.http import Response
from odoo import http
from odoo.http import request
import json
from datetime import date, datetime
# from slugify import slugify

from odoo.addons.das_publicfunction.controller.main import ProductInfo


class MainPageSectionHttp(http.Controller):
    @http.route('/api/main-page-section-http', type='http', auth="public", cors='*', methods=['Get'])
    def get_main_page_section(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            section_number = int(request.params.get('number'))
        except:
            section_number = False
         
        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = False
        if section_number:
            x_localization = request.httprequest.headers.get('x-localization')
            lang = "en"
            if x_localization:
                if x_localization == 'ar':
                    lang = "ar"

            if lang == "ar":
                if company_id:
                    section = request.env['main.page.section'].with_context(lang='ar_001').sudo().search(
                        [('section_number', '=', str(section_number)), ('company_id', '=', company_id)], limit=1)
                else:
                    section = request.env['main.page.section'].with_context(lang='ar_001').sudo().search(
                        [('section_number', '=', str(section_number))], limit=1)

            else:
                if company_id:
                    section = request.env['main.page.section'].sudo().search(
                        [('section_number', '=', str(section_number)), ('company_id', '=', company_id)], limit=1)
                else:
                    section = request.env['main.page.section'].sudo().search(
                        [('section_number', '=', str(section_number))], limit=1)
                # section = request.env['main.page.section'].sudo().search([('section_number', '=', str(section_number))])

            if section:

                ads_list = []
                product_list = []


                try:
                    user_id = int(request.params.get('user_id'))
                except:
                    user_id = False

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
                                             "product_image": base_url +  "/web/content/" + str(
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
                    "number":section.section_number,
                    "name": section.name if section.name else "",
                    # "slug_name": slugify(section.name) if section.name else "",
                    "image": base_url + "/web/content/" + str(
                        section.main_page_section_image_attachment.id) if section.main_page_section_image_attachment.id else "",
                    "product_ids": product_list,
                }

                Response.status = '200'
                response = {'status': 200, 'response': vals, 'message': 'List Of main page section Found'}
            else:


                Response.status = '200'

                response = {'status': 200, 'response': [],'message': 'No section Found'}
        else:

            Response.status = '200'

            response = {'status': 200, 'response': [],'message': 'No section Found'}
        # return response
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
