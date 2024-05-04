from odoo.http import request
from odoo.http import Response
import json
from odoo import http
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re


class PlatDeJoue(http.Controller):
    @http.route('/api/plat-du-jour', type='json', auth="public", cors='*', methods=['POST'])
    def get_plat_de_jour(self):
        req = json.loads(request.httprequest.data)
        try:
            day_of_week = req.get('day_of_week')
        except:
            day_of_week = -1

        try:
            company_id = req.get('company_id')
        except:
            company_id = False
            pass


        if day_of_week!=-1:
            x_localization = request.httprequest.headers.get('x-localization')
            lang = "en"
            if x_localization:
                if x_localization == 'ar':
                    lang = "ar"

            if lang == "ar":
                if company_id:
                    plat = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search(
                        [('day_of_week', '=', str(day_of_week)), ('company_id', 'in', [company_id,False])], limit=1)
                else:
                    plat = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search(
                        [('day_of_week', '=', str(day_of_week) )], limit=1)

            else:
                if company_id:
                    plat = request.env['plat.de.jour'].sudo().search(
                        [('day_of_week', '=', str(day_of_week)), ('company_id', 'in', [company_id,False])], limit=1)

                else:
                    plat = request.env['plat.de.jour'].sudo().search(
                        [('day_of_week', '=', str(day_of_week))], limit=1)

            slug_name = ""
            day_of_week_name = ""
            day_of_week_name_ar = ""
            if day_of_week == int('0'):
                slug_name = "monday"
                day_of_week_name = "Monday"
                day_of_week_name_ar = "الاثنين"
            elif day_of_week == int('1'):
                slug_name = "tuesday"
                day_of_week_name = "Tuesday"
                day_of_week_name_ar = "الثلاثاء"
            elif day_of_week == int('2'):
                slug_name = "wednesday"
                day_of_week_name = "Wednesday"
                day_of_week_name_ar = "الأربعاء"
            elif day_of_week == int('3'):
                slug_name = "thursday"
                day_of_week_name = "Thursday"
                day_of_week_name_ar = "الخميس"
            elif day_of_week == int('4'):
                slug_name = "friday"
                day_of_week_name = "Friday"
                day_of_week_name_ar = "الجمعة"
            elif day_of_week == int('5'):
                slug_name = "saturday"
                day_of_week_name = "Saturday"
                day_of_week_name_ar = "السبت"
            elif day_of_week == int('6'):
                slug_name = "sunday"
                day_of_week_name = "Sunday"
                day_of_week_name_ar = "الأحد"

            if plat:

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

                    for product in plat.product_ids:
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
                                                 "price_list": Product_Info.get_prices_for_currency_list(the_price,company_id),
                                                 'template_sale_price_new': new_price,
                                                 'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(new_price,company_id),
                                                 'template_sale_price_old': round(price_product, 2),
                                                 'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(price_product,company_id),
                                                 'percent_discount': percent_discount,
                                                 'is_fav': is_fav,
                                                 "category_id": product.categ_id.id,
                                                 "variant_discount": Product_Info.has_variant_discount(product.id,
                                                                                                       company_id)
                                                 })

                    vals = {
                        "id": plat.id,
                        "day_of_week": plat.day_of_week,
                        "slug_name": slug_name,
                        "day_of_week_name": day_of_week_name,
                        "day_of_week_name_ar": day_of_week_name_ar,
                        "name": plat.name if plat.name else "",
                        "image": "/web/content/" + str(
                            plat.plat_de_jour_image_attachment.id) if plat.plat_de_jour_image_attachment.id else "",
                        "product_ids": product_list,
                    }

                    Response.status = '200'
                    response = {'status': 200, 'response': vals, 'message': 'List Of plat de jour Found'}
            else:


                Response.status = '404'

                response = {'status': 404, 'message': 'No plat Found'}
        else:

            Response.status = '404'

            response = {'status': 404, 'message': 'No plat Found'}

        return response

    @http.route('/api/plat-du-jour-all', type='json', auth="public", cors='*', methods=['POST'])
    def get_plat_de_jour_all(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        req = json.loads(request.httprequest.data)
        try:
            day_of_week = req.get('day_of_week')
        except:
            day_of_week = -1

        try:
            company_id = req.get('company_id')
        except:
            company_id = False

        if day_of_week ==None:
            day_of_week = -1
        if company_id ==None:
            company_id = False
        try:
            user_id = req.get('user_id')
        except:
            user_id = False
        if user_id ==None:
            user_id = False
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if lang == "ar":
            if company_id:
                if day_of_week != -1:
                    plats = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search(
                        [('day_of_week', '=', str(day_of_week)), ('company_id', 'in', [company_id, False])], limit=1,order="day_of_week asc")
                else:
                    plats = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search(
                        [('company_id', 'in', [company_id, False])],order="day_of_week asc")
            else:
                if day_of_week != -1:
                    plats = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search(
                        [('day_of_week', '=', str(day_of_week))], limit=1,order="day_of_week asc")
                else:
                    plats = request.env['plat.de.jour'].with_context(lang='ar_001').sudo().search([],order="day_of_week asc")

        else:
            if company_id:
                if day_of_week != -1:
                    plats = request.env['plat.de.jour'].sudo().search(
                        [('day_of_week', '=', str(day_of_week)), ('company_id', 'in', [company_id, False])], limit=1,order="day_of_week asc")
                else:
                    plats = request.env['plat.de.jour'].sudo().search(
                        [('company_id', 'in', [company_id, False])],order="day_of_week asc")

            else:
                if day_of_week != -1:
                    plats = request.env['plat.de.jour'].sudo().search(
                        [('day_of_week', '=', str(day_of_week))], limit=1,order="day_of_week asc")
                else:
                    plats = request.env['plat.de.jour'].sudo().search([],order="day_of_week asc")
        

        if plats:

            ads_list = []
            product_list = []

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
            vals_list = []
            for plat in plats:


                product_list=[]
                for product in plat.product_ids:
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
                                             "category_id": product.categ_id.id
                                             })

                slug_name = ""
                day_of_week_name = ""
                day_of_week_name_ar = ""
                if plat.day_of_week=='0':
                    slug_name = "monday"
                    day_of_week_name ="Monday"
                    day_of_week_name_ar = "الاثنين"
                elif plat.day_of_week=='1':
                    slug_name = "tuesday"
                    day_of_week_name = "Tuesday"
                    day_of_week_name_ar = "الثلاثاء"
                elif plat.day_of_week=='2':
                    slug_name = "wednesday"
                    day_of_week_name = "Wednesday"
                    day_of_week_name_ar = "الأربعاء"
                elif plat.day_of_week=='3':
                    slug_name = "thursday"
                    day_of_week_name = "Thursday"
                    day_of_week_name_ar = "الخميس"
                elif plat.day_of_week=='4':
                    slug_name = "friday"
                    day_of_week_name = "Friday"
                    day_of_week_name_ar = "الجمعة"
                elif plat.day_of_week=='5':
                    slug_name = "saturday"
                    day_of_week_name = "Saturday"
                    day_of_week_name_ar = "السبت"
                elif plat.day_of_week=='6':
                    slug_name = "sunday"
                    day_of_week_name = "Sunday"
                    day_of_week_name_ar = "الأحد"

                vals = {
                    "id": plat.id,
                    "day_of_week": plat.day_of_week,
                    "slug_name" : slug_name,
                    "day_of_week_name": day_of_week_name,
                    "day_of_week_name_ar":day_of_week_name_ar,
                    "name": plat.name if plat.name else "",
                    "image":   "/web/content/" + str(
                        plat.plat_de_jour_image_attachment.id) if plat.plat_de_jour_image_attachment.id else "",
                    "product_ids": product_list,
                }
                vals_list.append(vals)

            day_list = ['0', '1', '2', '3', '4', '5', '6']
            for day in day_list:
                day_exist = False
                for val_l in vals_list:
                    if int(day) == int(val_l['day_of_week']):
                        day_exist = True

                        continue

                if day_exist == False:
                    slug_name = ""
                    day_of_week_name = ""
                    day_of_week_name_ar = ""
                    if day == '0':
                        slug_name = "monday"
                        day_of_week_name = "Monday"
                        day_of_week_name_ar = "الاثنين"
                    elif day == '1':
                        slug_name = "tuesday"
                        day_of_week_name = "Tuesday"
                        day_of_week_name_ar = "الثلاثاء"
                    elif day == '2':
                        slug_name = "wednesday"
                        day_of_week_name = "Wednesday"
                        day_of_week_name_ar = "الأربعاء"
                    elif day == '3':
                        slug_name = "thursday"
                        day_of_week_name = "Thursday"
                        day_of_week_name_ar = "الخميس"
                    elif day == '4':
                        slug_name = "friday"
                        day_of_week_name = "Friday"
                        day_of_week_name_ar = "الجمعة"
                    elif day == '5':
                        slug_name = "saturday"
                        day_of_week_name = "Saturday"
                        day_of_week_name_ar = "السبت"
                    elif day == '6':
                        slug_name = "sunday"
                        day_of_week_name = "Sunday"
                        day_of_week_name_ar = "الأحد"
                    vals = {
                        "id": 0,
                        "day_of_week": day,
                        "slug_name" : slug_name,
                        "day_of_week_name": day_of_week_name,
                        "day_of_week_name_ar": day_of_week_name_ar,
                        "name": "",
                        "image": "",
                        "product_ids": [],
                    }
                    vals_list.append(vals)

            Response.status = '200'
            sorted_data = sorted(vals_list, key=lambda x: x["day_of_week"])
            response = {'status': 200, 'response': sorted_data, 'message': 'List Of plat de jour Found'}
        else:

            Response.status = '404'

            response = {'status': 404, 'message': 'No plat Found'}

        return response


