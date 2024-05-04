from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
from datetime import date, datetime, timedelta
import requests
import itertools
import math
from itertools import product
import re
import pytz
from collections import defaultdict

class ProductInfo(http.Controller):

    def __init__(self):
        self.fire_base = self.get_server_token()
    def get_server_token(self):
        config = request.env['ir.config_parameter'].sudo()
        fire_base_api_key = config.get_param('das_res_config_settings.fire_base_api_key')
        return fire_base_api_key

    version = "/api/"
    ENCRYPTION_KEY = 0x135A
    asia_beirut = 'Asia/Beirut'
    beirut_timezone = pytz.timezone(asia_beirut)
    # server_Token = 'AAAAppIgW2o:APA91bGZRxL_hJCmRi2foL0QpZkaxMOonZcWq6GgqWORw62rA0mMJd3zrwo4oQuZ1kRp4BF40OrWnB4j_b3GzHRDtqgY2LXShLMvZlQR1hw2NVW4XWmIiXsXhEf7fH8GTFgbPtdZUDt_'
    server_Token = 'AAAAp4RfKZw:APA91bHTxm7maSfczp5NgjBmFJLT-SBMm8KoY0VYH9oQFpYF6Gc8MrnNdGgrD101IJ8DFgnUP0SqrpRcTbgF3aLnJWP_74sKgb6lHonUmHMHZHUrxJz5ihvMVBj8ezIoCbU6CF3uQ4lv'



    # def get_server_token(self):
    #     config = request.env['ir.config_parameter'].sudo()
    #     fire_base_api_key = config.get_param('das_res_config_settings.fire_base_api_key')
    #
    #     print('---------------------',fire_base_api_key)
    #     return fire_base_api_key

    def is_multi_company(self):
        companies = request.env['res.company'].sudo().search([])

        if len(companies) == 1:
            return False
        else:
            if self.is_multi_branch():
                return False
            else:
                return True

    def is_multi_branch(self):
        companies = request.env['res.company'].sudo().search([])
        multi_branch = False
        if len(companies) == 1:
            return True
        else:
            for company in companies:
                if company.parent_id:
                    multi_branch = True
                    break

            return multi_branch

    def get_the_full_product_product_name(self,product_product_id,lang):
        Product_Info = ProductInfo()
        if lang == 'ar':
            product_product = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                [('id', '=', product_product_id)])
        else:
            product_product = request.env['product.product'].sudo().search(
                [('id', '=', product_product_id)])

        thename = product_product.name

        variant_name = Product_Info.get_product_variant_name(product_product)

        if variant_name != '':
            variant_name = ' (' + variant_name + ')'
        if variant_name:
            thename = thename + variant_name

        return thename
    def create_kitchen_notes_new(self, notes, addons_note_list, removable_ingredients_note_list, combo_content_list,
                                 lang,product_initial):

        parent_name = ''

        add_word = 'add'
        remove_word = 'remove'
        client_note = 'Client Note : '

        if lang == 'ar':
            add_word = 'اضافة'
            remove_word = 'ازالة مكون'
            client_note = 'ملاحظة الزبون : '

        addons_dict = defaultdict(list)
        for addon in addons_note_list:
            addons_dict[addon["parent_id"]].append(addon["product_id"])

        remove_dict = defaultdict(list)
        for remove in removable_ingredients_note_list:
            remove_dict[remove["parent_id"]].append(remove["product_id"])

        # Merge the dictionaries into the desired format
        merged_list = []
        parent_ids = set(addons_dict.keys()).union(remove_dict.keys())

        for parent_id in parent_ids:
            merged_list.append({
                "parent_id": parent_id,
                "product_addons_ids": addons_dict[parent_id],
                "product_remove_ids": remove_dict[parent_id]
            })
        parent_name = ''
        for item in merged_list:

            product_remove_name = ''
            for product_id in item['product_remove_ids']:
                if product_remove_name == '':
                    product_remove_name = self.get_the_full_product_product_name(product_id, lang)
                else:
                    product_remove_name = self.get_the_full_product_product_name(product_id,
                                                                                 lang) + ',' + product_remove_name

            product_add_name = ''
            for product_id in item['product_addons_ids']:
                if product_add_name == '':
                    product_add_name = self.get_the_full_product_product_name(product_id, lang)
                else:
                    product_add_name = self.get_the_full_product_product_name(product_id, lang) + ',' + product_add_name


            if product_initial.is_combo:
                if parent_name == '':
                    parent_name = self.get_the_full_product_product_name(item['parent_id'], lang)
                else:
                    parent_name = parent_name + '\n' + self.get_the_full_product_product_name(item['parent_id'], lang)
            
            if product_add_name != '':
                if parent_name !='':
                    parent_name = parent_name + ' : (' + add_word + ':' + product_add_name
                else:
                    parent_name = '(' + add_word + ':' + product_add_name

                if product_remove_name != '':
                    parent_name = parent_name + ' , ' + remove_word + ':' + product_remove_name + ' )'


                else:
                    parent_name = parent_name + ' )'
            else:
                if product_remove_name != '':
                    if parent_name != '':
                        parent_name = parent_name + ' : (' + remove_word + ':' + product_remove_name + ' )'
                    else:
                        parent_name = '(' + remove_word + ':' + product_remove_name + ' )'

        combo_content = ''
        if combo_content_list:
            if len(combo_content_list) > 0:
                for content in combo_content_list:
                    attribute_value_name = ''
                    if lang == 'ar':
                        attribute_value = request.env['product.attribute.value'].with_context(lang='ar_001').sudo().search(
                            [('id', '=', content['value_value_id'])])
                    else:
                        attribute_value = request.env['product.attribute.value'].sudo().search(
                            [('id', '=', content['value_value_id'])])

                    if combo_content == '':
                        if attribute_value :
                            combo_content = self.get_the_full_product_product_name(content['product_id'],
                                                                               lang) + '(' + attribute_value.name + ')'
                        else:
                            combo_content = self.get_the_full_product_product_name(content['product_id'],
                                                                                   lang)
                    else:
                        if attribute_value:
                            combo_content = self.get_the_full_product_product_name(content['product_id'],
                                                                               lang) + '(' + attribute_value.name + ')' + ',' + combo_content
                        else:
                            combo_content = self.get_the_full_product_product_name(content['product_id'],
                                                                                   lang)   + ',' + combo_content



                if combo_content != '':
                    if parent_name != '':
                        parent_name = parent_name + '\n' + combo_content
                    else:
                        parent_name = combo_content

        if notes:
            if parent_name != '':
                parent_name = parent_name + '\n' + client_note + notes
            else:
                parent_name = parent_name + client_note + notes

        return parent_name

    @http.route(version + 'code-decode', type='json', auth='public', methods=['Post'], cors="*")
    def get_code_encode(self):
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')

        except:
            company_id = -1

        products_list = self.encode_number(company_id)
        message = self.decode_number(products_list)
        Response.status = '200'
        response = {'status': 200, 'response': products_list, 'message': message}
        return response

    def encode_number(self, number):
        # Convert the number to bytes and apply XOR-based encryption
        encrypted_data = ''.join([chr(ord(char) ^ self.ENCRYPTION_KEY) for char in str(number)])

        # Encode the encrypted data using Base64
        encoded_data = base64.b64encode(encrypted_data.encode('utf-8')).decode('utf-8')
        return encoded_data

    def decode_number(self, encoded_data):
        # Decode the Base64-encoded data
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')

        # Apply XOR-based decryption
        decrypted_data = ''.join([chr(ord(char) ^ self.ENCRYPTION_KEY) for char in decoded_data])
        return int(decrypted_data)

    def get_preparation_time(self, order):

        if order:
            max_preparation = 0
            for line in order.order_line:
                if line.product_id.preparing_time:
                    new_preparation = float(line.product_id.preparing_time)
                else:
                    new_preparation = 0
                if max_preparation < new_preparation:
                    max_preparation = new_preparation
            return int(max_preparation)
        else:
            return 0

    def format_time_from_float(self, float_time):
        # hours = int(float_time)
        # minutes = round((float_time - hours) * 60)
        # seconds = round(((float_time - hours) * 60 - minutes) * 60)
        # formatted_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # return formatted_time
        hours = int(float_time)
        minutes = round((float_time - hours) * 60)
        formatted_time = "{:02d}:{:02d}".format(hours, minutes)
        return formatted_time

    def change_parag_to_line(self, parag):
        if parag:
            desc = re.sub(r'<.*?>', ' ', parag)
            desc = desc.strip()
        else:
            desc = ''
        return desc

    @http.route(version + 'das-360', type='json', auth='public', methods=['Post'], cors="*")
    def get_all_products_template(self):
        products = request.env['product.template'].sudo().search([], order='id')
        products_list = []

        for product in products:
            values = {
                "id": product.id,
                "name": product.name,
                "company": product.company_id.name
            }
            products_list.append(values)
        Response.status = '200'
        response = {'status': 200, 'response': products_list, 'message': 'all products Found'}
        return response

    @http.route(version + 'config', type='json', auth='public', methods=['Post'], cors='*')
    def get_settings(self):
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
            if company_id:
                restaurant_name = request.env['res.company'].sudo().search([('id', '=', company_id)])
            else:
                restaurant_name = request.env['res.company'].sudo().search([], order='id', limit=1)
        except:
            restaurant_name = request.env['res.company'].sudo().search([], order='id', limit=1)

        if company_id:
            tax = request.env['account.tax'].sudo().search([('company_id', '=', company_id)])
        else:
            tax = request.env['account.tax'].sudo().search([], limit=1)

        # restaurant_name = request.env['res.company'].sudo().search([('id', '=', request.env.user.company_id.id)])
        if restaurant_name:
            calendar = request.env['resource.calendar'].sudo().search(
                [('company_id', '=', restaurant_name.id), ('active', '=', True)])

            has_delivery = False
            has_pickup = False
            try:
                has_pickup = restaurant_name.has_pickup
            except:
                has_pickup = False

            try:
                has_delivery = restaurant_name.has_delivery
            except:
                has_delivery = False

            restaurant_schedule_time = []
            if calendar:

                dayofweek_list = [0, 1, 2, 3, 4, 5, 6]
                for dayofweek in dayofweek_list:
                    open_close = []

                    calendar_attendance = request.env['resource.calendar.attendance'].sudo().search(
                        [('calendar_id', '=', calendar[0].id), ('dayofweek', '=', dayofweek)],
                        order='dayofweek ASC,hour_from ASC')
                    if calendar_attendance:
                        for att in calendar_attendance:
                            val = {
                                "opening_time": self.format_time_from_float(att.hour_from),
                                "closing_time": self.format_time_from_float(att.hour_to)
                            }
                            open_close.append(val)
                        values_att = {
                            "day_name": dict(att._fields['dayofweek'].selection).get(
                                att.dayofweek),
                            "day": dayofweek if dayofweek <= 6 else 0,
                            "opening_closing_time": open_close

                        }
                        restaurant_schedule_time.append(values_att)

            if tax:
                tva_enable = True
            else:
                tva_enable = False
            address = ''

            if restaurant_name.street:
                address = restaurant_name.street
            if restaurant_name.street2:
                if address != '':
                    address = address + ' ' + restaurant_name.street2
                else:
                    address = restaurant_name.street2
            try:
                if restaurant_name.category_title:
                    category_title = restaurant_name.category_title
                else:
                    category_title = ''

                if restaurant_name.category_image_attachment.id:
                    category_image_attachment = "/web/content/" + str(restaurant_name.category_image_attachment.id)
                else:
                    category_image_attachment = ''

            except:
                category_title = ""
                category_image_attachment = ""

            try:

                if restaurant_name.cart_title:
                    cart_title = restaurant_name.cart_title
                else:
                    cart_title = ''

                if restaurant_name.cart_image_attachment.id:
                    cart_image_attachment = "/web/content/" + str(
                        restaurant_name.cart_image_attachment.id)
                else:
                    cart_image_attachment = ''



            except:
                cart_title = ""
                cart_image_attachment = ""

            try:

                if restaurant_name.checkout_title:
                    checkout_title = restaurant_name.checkout_title
                else:
                    checkout_title = ''

                if restaurant_name.checkout_image_attachment.id:
                    checkout_image_attachment = "/web/content/" + str(
                        restaurant_name.checkout_image_attachment.id)
                else:
                    checkout_image_attachment = ''

            except:
                checkout_title = ""
                checkout_image_attachment = ""

            try:
                if restaurant_name.faq_banner_attachment.id:
                    faq_banner = "/web/content/" + str(
                        restaurant_name.faq_banner_attachment.id)
                else:
                    faq_banner = ''

            except:
                faq_banner = ""

            try:
                if restaurant_name.career_banner_attachment.id:
                    career_banner = "/web/content/" + str(
                        restaurant_name.career_banner_attachment.id)
                else:
                    career_banner = ''

            except:
                career_banner = ""

            try:
                if restaurant_name.deal_title1:
                    deal_title1 = restaurant_name.deal_title1
                else:
                    deal_title1 = ''

                if restaurant_name.deal_title2:
                    deal_title2 = restaurant_name.deal_title2
                else:
                    deal_title2 = ''

                if restaurant_name.deal_banner_image_attachment.id:
                    deal_banner = "/web/content/" + str(
                        restaurant_name.deal_banner_image_attachment.id)
                else:
                    deal_banner = ''

                if restaurant_name.deal_background_image_attachment.id:
                    deal_background = "/web/content/" + str(
                        restaurant_name.deal_background_image_attachment.id)
                else:
                    deal_background = ''

            except:
                deal_title1 = ""
                deal_title2 = ""
                deal_banner = ""
                deal_background = ""

            try:
                if restaurant_name.promotion_title:
                    promotion_title = restaurant_name.promotion_title
                else:
                    promotion_title = ''

                if restaurant_name.promotion_image_attachment.id:
                    promotion_banner = "/web/content/" + str(
                        restaurant_name.promotion_image_attachment.id)
                else:
                    promotion_banner = ''

                if restaurant_name.footer_image_attachment.id:
                    footer_banner = "/web/content/" + str(
                        restaurant_name.footer_image_attachment.id)
                else:
                    footer_banner = ''
            except:
                promotion_title = ""
                promotion_banner = ""
                footer_banner = ""

            company_banner = [{
                "category_title": category_title,
                "category_banner": category_image_attachment,

                "cart_title": cart_title,
                "cart_banner": cart_image_attachment,

                "checkout_title": checkout_title,
                "checkout_banner": checkout_image_attachment,
                "faq_banner": faq_banner,
                "career_banner": career_banner,

                "deal_title1": deal_title1,
                "deal_title2": deal_title2,
                "deal_banner": deal_banner,
                "deal_background": deal_background,

                "promotion_title": promotion_title,
                "promotion_banner": promotion_banner,
                "footer_banner": footer_banner,
            }]
            currency_list = []
            currency_active = calendar = request.env['res.currency'].sudo().search(
                [('active', '=', True), ('id', '!=', restaurant_name.currency_id.id)])
            for cur in currency_active:
                val_cur = {
                    "currency_symbol": cur.name,
                    "currency_symbol_en": cur.name,
                    "currency_id": cur.id
                }
                currency_list.append(val_cur)

            try:
                if restaurant_name.favicon_attachment.id:
                    restaurant_favicon = "/web/content/" + str(restaurant_name.favicon_attachment.id)
                else:
                    restaurant_favicon = ""
            except:
                restaurant_favicon = ""

            try:
                if restaurant_name.url_app_store:
                    url_app_store = restaurant_name.url_app_store
                else:
                    url_app_store = ""

                if restaurant_name.url_play_store:
                    url_play_store = restaurant_name.url_play_store
                else:
                    url_play_store = ""


            except:
                url_app_store = ""
                url_play_store = ""

            try:
                if restaurant_name.loader_image_attachment.id:
                    restaurant_loader_for_web_app = "/web/content/" + str(restaurant_name.loader_image_attachment.id)
                else:
                    restaurant_loader_for_web_app = ""

                if restaurant_name.splash_image_attachment.id:
                    splash_background_for_mobile_app = "/web/content/" + str(restaurant_name.splash_image_attachment.id)
                else:
                    splash_background_for_mobile_app = ""

            except:
                restaurant_loader_for_web_app = ""
                splash_background_for_mobile_app = ""

            restaurant_name_arabic = ""
            try:
                if restaurant_name.company_name_ar:
                    restaurant_name_arabic = restaurant_name.company_name_ar
                else:
                    restaurant_name_arabic = ""
            except:
                pass

            restaurant_address_arabic = ''
            try:
                if restaurant_name.street_ar:
                    restaurant_address_arabic = restaurant_name.street_ar
                if restaurant_name.street2_ar:
                    if restaurant_address_arabic != '':
                        restaurant_address_arabic = restaurant_address_arabic + ' ' + restaurant_name.street2_ar
                    else:
                        restaurant_address_arabic = restaurant_name.street2_ar
            except:
                pass
            values = {
                # "multi_branch":self.is_multi_branch(),
                # "multi_company":self.is_multi_company(),
                "company_id": restaurant_name.id,
                "restaurant_name": restaurant_name.name,
                "restaurant_name_arabic": restaurant_name_arabic,
                "restaurant_address": address,
                "restaurant_address_arabic": restaurant_address_arabic,
                "restaurant_phone": restaurant_name.phone if restaurant_name.phone else '',
                "restaurant_email": restaurant_name.email if restaurant_name.email else '',
                "currency_symbol": restaurant_name.currency_id.name,
                "currency_symbol_en": restaurant_name.currency_id.name,
                "currency_id": restaurant_name.currency_id.id,
                "currency_list": currency_list,
                "restaurant_logo": "/web/content/" + str(
                    restaurant_name.logo_web_attachment.id) if restaurant_name.logo_web_attachment.id else "",
                "restaurant_favicon": restaurant_favicon,
                # "restaurant_favicon": "/web/content/" + str(restaurant_name.favicon_attachment.id) if restaurant_name.favicon_attachment.id else "",
                "restaurant_schedule_time": restaurant_schedule_time,
                "social_media_link": {
                    "twitter": restaurant_name.social_twitter if restaurant_name.social_twitter else "",
                    "facebook": restaurant_name.social_facebook if restaurant_name.social_facebook else "",
                    "gitHub": restaurant_name.social_github if restaurant_name.social_github else "",
                    "linkedIn": restaurant_name.social_linkedin if restaurant_name.social_linkedin else "",
                    "youtube": restaurant_name.social_youtube if restaurant_name.social_youtube else "",
                    "instagram": restaurant_name.social_instagram if restaurant_name.social_instagram else "",
                    "whatsapp": restaurant_name.whatsapp if restaurant_name.whatsapp else "",
                },
                "company_banners": company_banner,
                # "main-page-banners": vals,
                # "about-us": vals_about_us,
                # "sign-in-up-banner": "/web/content/" + str(restaurant_name.sign_banner_attachment.id) if restaurant_name.sign_banner_attachment.id else "",
                "sign-in-up-banner": "",
                "tva_enable": tva_enable,
                "has_delivery": has_delivery,
                "has_pickup": has_pickup,
                "longitude": restaurant_name.partner_id.partner_longitude if restaurant_name.partner_id else 0.0,
                "latitude": restaurant_name.partner_id.partner_latitude if restaurant_name.partner_id else 0.0,
                "url_app_store": url_app_store,
                "url_play_store": url_play_store,
                "splash_background_for_mobile_app": splash_background_for_mobile_app,
                "restaurant_loader_for_web_app": restaurant_loader_for_web_app

            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Config Found'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}

        return response

    def get_prices_for_currency_list(self, price, company_id=None):
        currency_list = []
        if company_id:
            restaurant_name = request.env['res.company'].sudo().search([('id', '=', company_id)])
        else:
            restaurant_name = request.env['res.company'].sudo().search([], order='id', limit=1)

        currency_active = request.env['res.currency'].sudo().search(
            [('active', '=', True), ('id', '!=', restaurant_name.currency_id.id)])
        for cur in currency_active:
            val_cur = {
                "currency_symbol": cur.name,
                "currency_symbol_en": cur.name,
                "currency_id": cur.id,
                "price": round(price * self.get_currency_rate(cur.id, company_id), 2)
            }
            currency_list.append(val_cur)
        return currency_list

    def get_currency_rate(self, currency_id, company_id=None):
        try:
            if company_id:
                currency_rate = request.env['res.currency.rate'].sudo().search(
                    [('currency_id', '=', currency_id), ('company_id', '=', company_id)], order='name desc', limit=1)
            else:
                currency_rate = request.env['res.currency.rate'].sudo().search(
                    [('currency_id', '=', currency_id)], order='name desc', limit=1)
            if currency_rate:
                return currency_rate.rate
            else:
                return 0.0
        except:
            return 0.0

    @http.route(version + 'currency-rate', type='json', auth='public', methods=['Post'], cors='*')
    def get_currency_rate_api(self):
        try:
            req = json.loads(request.httprequest.data)
            currency_id = req.get('currency_id')
            try:
                company_id = req.get('company_id')
            except:
                company_id = False

            if company_id:
                if currency_id:
                    currency_rate = request.env['res.currency.rate'].sudo().search(
                        [('currency_id', '=', currency_id), ('company_id', '=', company_id)], order='name desc',
                        limit=1)

                    Response.status = '200'
                    response = {'status': 200, 'response': currency_rate.rate, 'message': 'Currency Found!'}

                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Currency not Found!'}
            else:

                if currency_id:
                    currency_rate = request.env['res.currency.rate'].sudo().search(
                        [('currency_id', '=', currency_id)], order='name desc', limit=1)

                    Response.status = '200'
                    response = {'status': 200, 'response': currency_rate.rate, 'message': 'Currency Found!'}

                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Currency not Found!'}
        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route(version + 'currency-rate-list', type='json', auth='public', methods=['Post'], cors='*')
    def get_currency_rate_list_api(self):
        try:
            req = json.loads(request.httprequest.data)

            try:
                company_id = req.get('company_id')
            except:
                company_id = False

            currency_list = []
            if company_id:
                restaurant_name = request.env['res.company'].sudo().search([('id', '=', company_id)])
            else:
                restaurant_name = request.env['res.company'].sudo().search([], order='id', limit=1)

            currency_active = request.env['res.currency'].sudo().search(
                [('active', '=', True), ('id', '!=', restaurant_name.currency_id.id)])

            for cur in currency_active:
                val_cur = {
                    "currency_symbol": cur.name,
                    "currency_symbol_en": cur.name,
                    "currency_id": cur.id,
                    "rate": self.get_currency_rate(cur.id, restaurant_name.id)
                }
                currency_list.append(val_cur)

            Response.status = '200'
            response = {'status': 200, 'currency_list': currency_list, 'message': 'Currency Found!'}

        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    def get_add_ons(self, product_template,lang):
        product_add_ons_list = []

        add_ons = product_template.product_addons_ids

        for add_on in add_ons:
            # values_add_ons = self.get_product_product_details(add_on)

            if lang == 'ar':
                product_product = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                    [('id', '=', add_on.id)])
            else:
                product_product = request.env['product.product'].sudo().search(
                    [('id', '=', add_on.id)])

            values_add_ons = self.get_product_full_product_details(product_product,lang)
            # values_add_ons = self.get_product_full_product_details(add_on)

            product_add_ons_list.append(values_add_ons)

        return product_add_ons_list

    def get_ingredients(self, product_template,lang):
        product_ingredient_list = []

        ingredients = product_template.ingredient_ids

        for ingredient in ingredients:
            # values_ingredient = self.get_product_product_details(ingredient)
            values_ingredient = self.get_product_full_product_details(ingredient,lang)
            product_ingredient_list.append(values_ingredient)

        return product_ingredient_list

    def get_removale_ingredients(self, product_template,lang):
        product_removable_ingredient_list = []

        removable_ingredients = product_template.removable_ingredient_ids

        for removable_ingredient in removable_ingredients:
            # values_removable_ingredient = self.get_product_product_details(removable_ingredient)
            values_removable_ingredient = self.get_product_full_product_details(removable_ingredient,lang)
            product_removable_ingredient_list.append(values_removable_ingredient)

        return product_removable_ingredient_list

    def get_related_product(self, product_template,lang):

        products = []
        if product_template:
            for relt in product_template.related_ids:
                default = False
                related = self.get_product_full_product_sd_details(relt, default,lang)
                products.append(related)

        return products

    def get_sides_product(self, product_template,lang):

        products = []
        if product_template:
            for relt in product_template.sides_ids:
                # values_removable_ingredient = self.get_product_product_details(removable_ingredient)
                # default = True if product_template.default_sides_id.id == relt.id else False
                side = self.get_product_full_product_sd_details(relt, False,lang)
                products.append(side)

        return products

    def get_product_product_sd_details(self, product_product, name_add=None, Price_add=None, default=None,value_value_id = None):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        variant_name = self.get_product_variant_name(product_product)
        if variant_name != '':
            variant_name = ' (' + variant_name + ')'

        if name_add:
            variant_name = variant_name + '(' + name_add + ')'

        if Price_add:
            price = product_product.lst_price + Price_add
        else:
            price = product_product.lst_price

        try:
            res = product_product.taxes_id.compute_all(price, product=product_product)
            included = res['total_included']
            price_product = included
        except:
            price_product = price

        the_price = self.get_product_product_price(product_product, price_product)
        price_without_TVA = self.get_product_product_price(product_product, price)

        if product_product.product_tmpl_id.company_id:
            thecompany_id = product_product.product_tmpl_id.company_id.id
        else:
            thecompany_id = False

        print('-==============value_value_id======================',value_value_id)
        values_prod = {
            "product_id": product_product.id,
            "product_templ_id": product_product.product_tmpl_id.id,
            "product_name": product_product.name + variant_name,
            "value_value_id":value_value_id if value_value_id else -1,
            "price": the_price,
            "price_list": self.get_prices_for_currency_list(the_price, thecompany_id),
            "price_without_TVA": round(price_without_TVA, 2),
            "price_without_TVA_list": self.get_prices_for_currency_list(price_without_TVA, thecompany_id),
            "product_image": "/web/content/" + str(product_product.product_tmpl_id.image_attachment.id) if str(
                product_product.product_tmpl_id.image_attachment.id) else "",
            "product_image_path": base_url + "/web/content/" + str(
                product_product.product_tmpl_id.image_attachment.id) if str(
                product_product.product_tmpl_id.image_attachment.id) else "",
            "product_main_image_path": base_url + "/web/content/" + str(
                product_product.product_tmpl_id.image_attachment.id) if str(
                product_product.product_tmpl_id.image_attachment.id) else "",
            "default": default
        }
        return values_prod

    def get_product_full_product_sd_details(self, product_product, default,lang):
        product_variant_list = []

        attribute_product_nevers = self.get_attribute_product_never(product_product.product_tmpl_id,lang)

        if len(attribute_product_nevers) > 0:
            combinations = self.generate_combinations(attribute_product_nevers)

            for combination in combinations:
                values_prod = self.get_product_product_sd_details(product_product, combination['name'],
                                                                  combination['price'], default)
                product_variant_list.append(values_prod)
        else:
            values_prod = self.get_product_product_sd_details(product_product, '', 0, default)
            product_variant_list.append(values_prod)

        return product_variant_list

    def get_drinks_product(self, product_template,lang):

        products = []
        if product_template:
            for relt in product_template.drinks_ids:
                # default = True if product_template.default_drink_id.id == relt.id else False
                drinks = self.get_product_full_product_sd_details(relt, False,lang)
                products.append(drinks)

        return products

    def get_desserts_product(self, product_template,lang):

        products = []
        if product_template:
            for relt in product_template.desserts_ids:
                default = False
                desserts = self.get_product_full_product_sd_details(relt, default,lang)
                products.append(desserts)

        return products

    def get_also_like_product(self, product_template,lang):

        products = []
        if product_template:
            for relt in product_template.liked_ids:
                default = False
                liked = self.get_product_full_product_sd_details(relt, default,lang)
                products.append(liked)

        return products

    def generate_combinations(self, input_data):
        attribute_value_lists = [attribute['value_list'] for attribute in input_data]
        all_combinations = list(product(*attribute_value_lists))

        formatted_combinations = []

        for combination in all_combinations:
            attributes_with_prices = zip(input_data, combination)
            names = []
            total_price = 0.0

            for attribute, value in attributes_with_prices:
                names.append(f"{value['value_name']}")
                total_price += value['value_price']

            formatted_combination = {"value_value_id": value['value_value_id'],"name": ', '.join(names), "price": total_price}
            formatted_combinations.append(formatted_combination)

        return formatted_combinations

    def get_product_template_details(self, product_template, lang):

        product_variant_list = []
        if lang == 'ar':
            product_products = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                [('product_tmpl_id', '=', product_template.id)])
        else:
            product_products = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        if product_template.is_combo:
            for product_product in product_products:
                values_prod = self.get_product_product_details(product_product, '', 0)
                product_variant_list.append(values_prod)
        else:
            attribute_product_nevers = self.get_attribute_product_never(product_template, lang)

            if len(attribute_product_nevers) > 0:
                print('---attribute_product_nevers--------------------', attribute_product_nevers)
                combinations = self.generate_combinations(attribute_product_nevers)

                print('---combinations-------combinations----------',combinations)
                for combination in combinations:

                    for product_product in product_products:
                        values_prod = self.get_product_product_details(product_product, combination['name'],
                                                                       combination['price'],combination['value_value_id'])
                        product_variant_list.append(values_prod)

            else:

                for product_product in product_products:
                    values_prod = self.get_product_product_details(product_product, '', 0)

                    product_variant_list.append(values_prod)

        return product_variant_list

    def get_product_full_product_details(self, product_product,lang):
        product_variant_list = []

        attribute_product_nevers = self.get_attribute_product_never(product_product.product_tmpl_id,lang)

        if len(attribute_product_nevers) > 0:
            combinations = self.generate_combinations(attribute_product_nevers)

            for combination in combinations:
                values_prod = self.get_product_product_details(product_product, combination['name'],
                                                               combination['price'],combination['value_value_id'])
                product_variant_list.append(values_prod)
        else:
            values_prod = self.get_product_product_details(product_product, '', 0)
            product_variant_list.append(values_prod)
        return product_variant_list

    def has_variant_discount(self, product_template_id, company_id):
        variant_discount = False

        if company_id:
            published_ads = request.env['price.list.variant'].sudo().search(
                [('is_published', '=', True), ('company_id', 'in', [company_id, False])])
        else:
            published_ads = request.env['price.list.variant'].sudo().search(
                [('is_published', '=', True)])

        if published_ads:

            for ad in published_ads:

                for line in ad.detail_fields:
                    if line.product_id.product_tmpl_id.id == product_template_id:
                        return True
        return variant_discount

    def get_product_variant_name(self, product_product):
        product_variant_name = ''
        variant_attribute = []

        if product_product.product_template_variant_value_ids:

            for variant in product_product.product_template_variant_value_ids:
                # product_variant_name = product_variant_name + ',' + variant.attribute_id.name + ':' + variant.name
                product_variant_name = product_variant_name + ',' + variant.name
            if product_variant_name != '':
                product_variant_name = product_variant_name[1:]
            else:
                product_variant_name = product_product.name
        else:
            product_variant_name = ''

        # wassim add this code
        # if product_variant_name == '':
        #     product_variant_name = product_product.name
        return product_variant_name

    def get_product_product_details(self, product_product, name_add=None, Price_add=None,value_value_id = None):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        product_variant_name = ''
        variant_attribute = []

        extra_price = 0

        if product_product.product_template_variant_value_ids:

            for attribute_value in product_product.product_template_attribute_value_ids:
                extra_price = extra_price + attribute_value.price_extra

            for variant in product_product.product_template_variant_value_ids:
                values_variant_attribute = {
                    "attribute_id": variant.attribute_id.id,
                    "attribute_name": variant.attribute_id.name,
                    "attribute_value_id": variant.product_attribute_value_id.id,
                    "attribute_value_name": variant.name,

                }
                # product_variant_name = product_variant_name + ',' + variant.attribute_id.name + ':' + variant.name
                product_variant_name = product_variant_name + ',' + variant.name
                variant_attribute.append(values_variant_attribute)

            if product_variant_name != '':
                product_variant_name = product_variant_name[1:]
            else:
                product_variant_name = product_product.name

        else:

            product_variant_name = product_product.name

        if product_product.detailed_type == "product":
            storable = True
        else:
            storable = False

        variant_name = self.get_product_variant_name(product_product)

        if name_add:
            if variant_name:
                variant_name = variant_name + ',' + name_add
            else:
                variant_name = name_add

        if variant_name != '':
            variant_name = ' (' + variant_name + ')'

        if Price_add:
            price = product_product.lst_price + Price_add
        else:
            price = product_product.lst_price

        try:
            res = product_product.taxes_id.compute_all(price, product=product_product)
            included = res['total_included']
            price_product = included
        except:
            price_product = price

        the_final_price = self.get_product_product_price(product_product, price_product)
        the_final_price_Without_TVA = self.get_product_product_price(product_product, price)

        if product_product.product_tmpl_id.company_id:
            thecompany_id = product_product.product_tmpl_id.company_id.id
        else:
            thecompany_id = False

        thename = product_product.name
        if variant_name:
            thename = thename + variant_name

        values_prod = {
            "product_product_id": product_product.id,
            "product_templ_id": product_product.product_tmpl_id.id,
            "product_variant_name": thename,
            "product_description": self.change_parag_to_line(
                product_product.product_tmpl_id.description_sale) if product_product.product_tmpl_id.description_sale else "",
            "value_value_id": value_value_id if value_value_id else -1,
            "default": product_product.default,
            "storable": storable,
            "product_sale_price": price_product,
            "product_sale_price_list": self.get_prices_for_currency_list(price_product, thecompany_id),
            "final_price": the_final_price,
            "final_price_list": self.get_prices_for_currency_list(the_final_price, thecompany_id),
            "final_price_Without_TVA": the_final_price_Without_TVA,
            "final_price_Without_TVA_list": self.get_prices_for_currency_list(the_final_price_Without_TVA,
                                                                              thecompany_id),
            "product_image": "/web/content/" + str(
                product_product.product_tmpl_id.image_attachment.id) if product_product.product_tmpl_id.image_attachment.id else "",
            "product_image_path": base_url + "/web/content/" + str(
                product_product.product_tmpl_id.image_attachment.id) if product_product.product_tmpl_id.image_attachment.id else "",
            "product_main_image_path": base_url + "/web/content/" + str(
                product_product.product_tmpl_id.image_attachment.id) if product_product.product_tmpl_id.image_attachment.id else "",
            'variant_attribute_list': variant_attribute
        }

        return values_prod

    def get_attribute_product_never(self, product_template,lang ):

        # product_attribute = request.env['product.template.attribute.line'].sudo().search(
        #     [('product_tmpl_id', '=', product_template.id)])

        if lang == "ar":
            product_attribute = request.env['product.template.attribute.line'].with_context(lang='ar_001').sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        else:
            product_attribute = request.env['product.template.attribute.line'].sudo().search(
                [('product_tmpl_id', '=', product_template.id)])


        if product_template.company_id:
            thecompany_id = product_template.company_id.id
        else:
            thecompany_id = False

        attribute_list = []
        if product_attribute:
            for att in product_attribute:
                value_list = []
                if att.attribute_id.create_variant == 'no_variant':
                    if lang == "ar":
                        att_values = request.env['product.template.attribute.value'].with_context(lang='ar_001').sudo().search(
                            [('attribute_line_id', '=', att.id), ('ptav_active', '=', True)])
                    else:
                        att_values = request.env['product.template.attribute.value'].sudo().search(
                            [('attribute_line_id', '=', att.id), ('ptav_active', '=', True)])
                    if att_values:
                        for att_value in att_values:
                            values = {
                                "value_value_id" : att_value.product_attribute_value_id.id,
                                "value_name": att_value.product_attribute_value_id.name,
                                "value_price": att_value.price_extra,
                                "value_price_list": self.get_prices_for_currency_list(att_value.price_extra,
                                                                                      thecompany_id)
                            }
                            value_list.append(values)

                    values_prod = {
                        "attribute_id": att.attribute_id.id,
                        # "attribute_name": att.attribute_id.name,
                        "value_list": value_list
                    }
                    attribute_list.append(values_prod)

        return attribute_list

    def get_attribute_product_product(self, product_product, lang):

        attribute_list = []
        if product_product.combination_indices:
            product_template_attribute_value_ids = []

            if product_product.product_tmpl_id.company_id:
                thecompany_id = product_product.product_tmpl_id.company_id.id
            else:
                thecompany_id = False

            product_template_attribute_value_ids = product_product.combination_indices.split(",")  # Split by comma

            product_template_attribute_values = request.env['product.template.attribute.value'].sudo().search(
                [('id', 'in', product_template_attribute_value_ids)])

            if product_template_attribute_values:

                for product_template_attribute_value in product_template_attribute_values:
                    price = 0
                    value_list = []
                    if lang == "ar":
                        att_value = request.env['product.attribute.value'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', product_template_attribute_value.product_attribute_value_id.id)])
                    else:
                        att_value = request.env['product.attribute.value'].sudo().search(
                            [('id', '=', product_template_attribute_value.product_attribute_value_id.id)])

                    if lang == "ar":
                        att = request.env['product.attribute'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', product_template_attribute_value.attribute_id.id)])
                    else:
                        att = request.env['product.attribute'].sudo().search(
                            [('id', '=', product_template_attribute_value.attribute_id.id)])

                    if product_template_attribute_value.ptav_active:
                        price = price + product_template_attribute_value.price_extra

                    default = True

                    val_att = {
                        "value_id": att_value.id,
                        "value_name": att_value.name,
                        "value_price": price,
                        "value_price_list": self.get_prices_for_currency_list(price, thecompany_id),
                        "default": default,

                    }
                    value_list.append(val_att)

                    values_prod = {
                        "attribute_id": att.id,
                        "attribute_name": att.name,
                        "value_list": value_list
                    }
                    attribute_list.append(values_prod)

        return attribute_list

    def get_attribute_product_product_as_mannasat(self, product_product, lang):

        attribute_list = []

        if product_product.combination_indices:
            product_template_attribute_value_ids = []
            if product_product.product_tmpl_id.company_id:
                thecompany_id = product_product.product_tmpl_id.company_id.id
            else:
                thecompany_id = False

            product_template_attribute_value_ids = product_product.combination_indices.split(",")  # Split by comma

            product_template_attribute_values = request.env['product.template.attribute.value'].sudo().search(
                [('id', 'in', product_template_attribute_value_ids)])

            if product_template_attribute_values:

                for product_template_attribute_value in product_template_attribute_values:
                    price = 0
                    value_list = []
                    if lang == "ar":
                        att_value = request.env['product.attribute.value'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', product_template_attribute_value.product_attribute_value_id.id)])
                    else:
                        att_value = request.env['product.attribute.value'].sudo().search(
                            [('id', '=', product_template_attribute_value.product_attribute_value_id.id)])

                    if lang == "ar":
                        att = request.env['product.attribute'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', product_template_attribute_value.attribute_id.id)])
                    else:
                        att = request.env['product.attribute'].sudo().search(
                            [('id', '=', product_template_attribute_value.attribute_id.id)])

                    if product_template_attribute_value.ptav_active:
                        price = price + product_template_attribute_value.price_extra

                    default = True

                    val_att = {
                        "value_id": att_value.id,
                        "label": att_value.name,
                        "optionPrice": price,
                        "optionPrice_list": self.get_prices_for_currency_list(price, thecompany_id),

                    }
                    value_list.append(val_att)

                    values_prod = {
                        "id": att.id,
                        "name": att.name,
                        "type": "multi",
                        "min": "1",
                        "max": "3",
                        "required": "off",
                        "values": value_list
                    }
                    attribute_list.append(values_prod)

        return attribute_list

    def get_attribute_product(self, product_template, lang):

        product_default = request.env['product.product'].sudo().search(
            [('product_tmpl_id', '=', product_template.id), ('default', '=', True)])

        if lang == "ar":
            product_attribute = request.env['product.template.attribute.line'].with_context(
                lang='ar_001').sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        else:
            product_attribute = request.env['product.template.attribute.line'].sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        if product_template.company_id:
            thecompany_id = product_template.company_id.id
        else:
            thecompany_id = False

        attribute_list = []
        if product_attribute:
            for att in product_attribute:
                value_list = []
                if lang == "ar":
                    att_value = request.env['product.attribute.value'].with_context(
                        lang='ar_001').sudo().search(
                        [('attribute_id', '=', att.attribute_id.id)])
                else:
                    att_value = request.env['product.attribute.value'].sudo().search(
                        [('attribute_id', '=', att.attribute_id.id)])

                for val in att_value:
                    product_template_attribute_value = request.env['product.template.attribute.value'].sudo().search(
                        [
                            ('attribute_id', '=', att.attribute_id.id),
                            ('product_attribute_value_id', '=', val.id),
                            ('product_tmpl_id', '=', product_template.id)
                        ])
                    if product_template_attribute_value:
                        if product_template_attribute_value[0].ptav_active:
                            price = product_template_attribute_value[0].price_extra
                        else:
                            price = 0
                    else:
                        price = 0
                    default = False
                    if product_default:
                        for variant in product_default.product_template_variant_value_ids:
                            if att.attribute_id.id == variant.attribute_id.id:
                                attribute_value = request.env['product.template.attribute.value'].sudo().search(
                                    [('id', '=', variant.id)])[0]
                                if val.id == attribute_value.product_attribute_value_id.id:
                                    default = True

                    val_att = {
                        "value_id": val.id,
                        "value_name": val.name,
                        "value_price": price,
                        "value_price_list": self.get_prices_for_currency_list(price, thecompany_id),
                        "default": default,

                    }
                    value_list.append(val_att)

                values_prod = {
                    "attribute_id": att.attribute_id.id,
                    "attribute_name": att.attribute_id.name,
                    "value_list": value_list
                }
                attribute_list.append(values_prod)

        return attribute_list

    def get_product_contents(self, product_template, lang):

        products = []
        if product_template:
            mrps = request.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', product_template.id)],
                                                        order='sequence,create_date,id',
                                                        limit=1)
            if mrps:
                for mrp in mrps:
                    lines = request.env['mrp.bom.line'].sudo().search([('bom_id', '=', mrp.id)])
                    if lines:
                        for line in lines:

                            if lang == "ar":
                                product_id = request.env['product.product'].with_context(lang='ar_001').sudo().search(
                                    [('id', '=', line.product_id.id)])

                            else:
                                product_id = request.env['product.product'].sudo().search(
                                    [('id', '=', line.product_id.id)])

                            values_content = self.get_product_full_product_details(product_id,lang)

                            for value_c in values_content:
                                value_c['product_product_info'] = self.get_product_product_information_by_id(
                                    product_id,lang)
                            products.append(values_content)

        return products

    def get_product_product_information_by_id(self, product_id,lang):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        values = {}

        if product_id.product_tmpl_id.company_id:
            thecompany_id = product_id.product_tmpl_id.company_id.id
        else:
            thecompany_id = False

        if product_id:
            the_template_sale_price = self.get_product_template_price(product_id.product_tmpl_id)
            values = {
                "product_id": product_id.id,
                "product_templ_id": product_id.product_tmpl_id.id,
                "product_name": product_id.name,
                "product_description": product_id.description_sale,
                "product_main_image": "/web/content/" + str(product_id.product_tmpl_id.image_attachment.id),
                "product_main_image_path": base_url + "/web/content/" + str(
                    product_id.product_tmpl_id.image_attachment.id),
                'template_sale_price': the_template_sale_price,
                'template_sale_price_list': self.get_prices_for_currency_list(the_template_sale_price, thecompany_id),
                'product_product_details': self.get_product_full_product_details(product_id,lang),  #########
                'Addons_details': self.get_add_ons(product_id.product_tmpl_id,lang),
                'Ingredients_details': self.get_ingredients(product_id.product_tmpl_id,lang),
                'Removable_Ingredients_details': self.get_removale_ingredients(product_id.product_tmpl_id,lang),

            }

        return values

    def get_attribute_product_new(self, product_template, lang):

        product_default = request.env['product.product'].sudo().search(
            [('product_tmpl_id', '=', product_template.id), ('default', '=', True)])

        if lang == "ar":
            product_attribute = request.env['product.template.attribute.line'].with_context(
                lang='ar_001').sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        else:
            product_attribute = request.env['product.template.attribute.line'].sudo().search(
                [('product_tmpl_id', '=', product_template.id)])

        if product_template.company_id:
            thecompany_id = product_template.company_id.id
        else:
            thecompany_id = False

        amount_TVA_Percent = 0
        for tax in product_template.taxes_id:
            amount_TVA_Percent = tax.amount

        attribute_list = []
        if product_attribute:
            for att in product_attribute:
                value_list = []
                if lang == "ar":
                    att_value = request.env['product.template.attribute.value'].with_context(
                        lang='ar_001').sudo().search(
                        [('attribute_line_id', '=', att.id), ('ptav_active', '=', True)])
                else:
                    att_value = request.env['product.template.attribute.value'].sudo().search(
                        [('attribute_line_id', '=', att.id), ('ptav_active', '=', True)])

                for val in att_value:
                    if val.ptav_active:

                        price = val.price_extra
                    else:
                        price = 0
                    # else:
                    #     price = 0
                    default = False
                    if product_default:

                        for variant in product_default.product_template_variant_value_ids:
                            if val.id == variant.id:
                                default = True

                    if amount_TVA_Percent != 0:
                        price_TVA = round(price * (1 + amount_TVA_Percent / 100), 2)
                    else:
                        price_TVA = price

                    val_att = {
                        "value_id": val.product_attribute_value_id.id,
                        "value_name": val.product_attribute_value_id.name,
                        "value_price": round(price_TVA, 2),
                        "value_price_list": self.get_prices_for_currency_list(price_TVA, thecompany_id),
                        "value_price_without_TVA": round(price, 2),
                        "value_price_without_TVA_list": self.get_prices_for_currency_list(price, thecompany_id),
                        "default": default,

                    }
                    value_list.append(val_att)

                values_prod = {
                    "attribute_id": att.attribute_id.id,
                    "attribute_name": att.attribute_id.name,
                    "value_list": value_list
                }
                attribute_list.append(values_prod)

        return attribute_list

    def get_product_product_variant_name(self, product_product):
        product_variant_name = ''
        variant_attribute = []

        if product_product.product_template_variant_value_ids:

            for variant in product_product.product_template_variant_value_ids:
                product_variant_name = product_variant_name + ',' + variant.attribute_id.name + ':' + variant.name

            if product_variant_name != '':
                product_variant_name = product_variant_name[1:]
            else:
                product_variant_name = product_product.name

        else:
            product_variant_name = product_product.name

        return product_variant_name

    def get_product_product_price(self, product_product, price_new=None):

        price = self.get_product_product_banner_price(product_product, price_new)
        if price is not None and price >= 0.0:
            return round(price, 2)
        else:
            price =   self.get_product_product_promotion_price(product_product, price_new)
            if price is not None and price >= 0.0:
                return round(price, 2)
            else:

                price = self.get_product_product_offer_price(product_product, price_new)

                if price is not None and price >= 0.0:
                    return round(price, 2)
                else:


                    price = self.get_product_variant_discount_price(product_product, price_new)

                    if price is not None and price >= 0.0:
                        return round(price, 2)
                    else:
                        if price_new:
                            return round(price_new, 2)
                        else:
                            return round(product_product.lst_price, 2)

    def get_product_variant_discount_price(self, product_product, price_new=None):
        try:

            price_lists = request.env['price.list.variant'].sudo().search(
                [('is_published', '=', True)])

            if price_new:
                shelf_price = price_new
            else:
                shelf_price = product_product.lst_price

            discount = request.env['price.list.variant.detail'].sudo().search(
                [('price_list_variant_id', 'in', price_lists.ids), ('product_id', '=', product_product.id)],
                order='write_date desc', limit=1)


            if discount:
                offer_price = shelf_price - ((discount.discount / 100) * shelf_price)

                return offer_price
            else:
                return shelf_price

        except:
            print("An error occurred:", e)
            return -1.0
        return -1.0

    def get_product_product_offer_price(self, product_product, price_new=None):
        try:
            product = request.env['product.template'].sudo().search(
                [('id', '=', product_product.product_tmpl_id.id)])

            offer_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_offer', '=', True)])

            if price_new:
                shelf_price = price_new
            else:
                shelf_price = product_product.lst_price

            offer_price = -1.0

            if offer_banners:
                for line in offer_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:

                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return offer_price
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product in products_ids:
                            offer_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return offer_price
                    elif line.applied_on == '3_global':
                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return offer_price
        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def get_product_product_banner_price(self, product_product, price_new=None):
        # try:
        #     product = request.env['product.template'].sudo().search(
        #         [('id', '=', product_product.product_tmpl_id.id)])
        #
        #     published_banners = request.env['product.pricelist'].sudo().search(
        #         [('is_published', '=', True), ('is_banner', '=', True)])
        #
        #     if price_new:
        #         shelf_price = price_new
        #     else:
        #         shelf_price = product_product.lst_price
        #     banner_price =  -1.0
        #
        #     if published_banners:
        #         for line in published_banners.item_ids:
        #             if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
        #                 banner_price = shelf_price - (
        #                         (line.percent_price / 100) * shelf_price)
        #                 return banner_price
        #             elif line.applied_on == '2_product_category':
        #                 category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
        #                 products_ids = request.env['product.template'].sudo().search(
        #                     [('categ_id', '=', category_id.id)])
        #                 if product in products_ids:
        #                     banner_price = shelf_price - (
        #                             (line.percent_price / 100) * shelf_price)
        #                     return banner_price
        #             elif line.applied_on == '3_global':
        #                 banner_price = shelf_price - (
        #                         (line.percent_price / 100) * shelf_price)
        #                 return banner_price
        # except:
        #     return -1.0
        try:
            product = request.env['product.template'].sudo().search(
                [('id', '=', product_product.product_tmpl_id.id)])

            published_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_banner', '=', True)])

            if price_new:
                shelf_price = price_new
            else:
                shelf_price = product_product.lst_price
            banner_price = -1.0

            if published_banners:
                for line in published_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return banner_price
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product in products_ids:
                            banner_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return banner_price
                    elif line.applied_on == '3_global':
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return banner_price
        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def get_product_product_promotion_price(self, product_product, price_new=None):
        try:
            product = request.env['product.template'].sudo().search(
                [('id', '=', product_product.product_tmpl_id.id)])

            # published_promotions = request.env['product.pricelist'].sudo().search(
            #     [('is_published', '=', True), ('is_promotion', '=', True)])

            if product_product.product_tmpl_id.company_id:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True),
                     ('company_id', 'in', [product_product.product_tmpl_id.company_id.id, False])])
            else:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True)])

            if price_new:
                shelf_price = price_new
            else:
                shelf_price = product_product.lst_price

            promotion_price =  -1.0

            if published_promotions:
                for line in published_promotions.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:

                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return promotion_price
                    elif line.applied_on == '2_product_category':

                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product in products_ids:
                            promotion_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return promotion_price
                    elif line.applied_on == '3_global':
                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return promotion_price
        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def get_product_template_price(self, product_template):
        try:
            res = product_template.taxes_id.compute_all(product_template.list_price, product=product_template)
            included = res['total_included']
            price_product = included
        except:
            price_product = product_template.list_price

        price = self.get_product_template_banner_price(product_template, price_product)
        if price is not None and price >= 0.0:
            return round(price, 2)
        else:
            price = self.get_product_template_promotion_price(product_template, price_product)
            if price is not None and price >= 0.0:
                return round(price, 2)
            else:

                price = self.get_product_template_offer_price(product_template, price_product)

                if price is not None and price >= 0.0:
                    return round(price, 2)
                else:
                    return round(price_product, 2)

    def get_product_template_price_without_TVA(self, product_template):

        price_product = product_template.list_price

        price = self.get_product_template_banner_price(product_template, price_product)
        if price:
            return round(price, 2)
        else:
            price = self.get_product_template_promotion_price(product_template, price_product)
            if price:
                return round(price, 2)
            else:

                price = self.get_product_template_offer_price(product_template, price_product)

                if price:
                    return round(price, 2)
                else:
                    return round(price_product, 2)

    def get_product_template_offer_price(self, product_template, price_product):

        try:
            offer_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_offer', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price
            offer_price = False

            if offer_banners:
                for line in offer_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:

                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return offer_price
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            offer_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return offer_price
                    elif line.applied_on == '3_global':
                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return offer_price


        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def get_product_template_banner_price(self, product_template, price_product):
        try:
            published_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_banner', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price
            banner_price = False

            if published_banners:
                for line in published_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return banner_price
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            banner_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return banner_price
                    elif line.applied_on == '3_global':
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return banner_price

        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def get_product_template_promotion_price(self, product_template, price_product):

        try:
            if product_template.company_id:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True),
                     ('company_id', 'in', [product_template.company_id.id, False])])
            else:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price

            promotion_price = False

            if published_promotions:
                for line in published_promotions.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:
                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return promotion_price
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            promotion_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            return promotion_price
                    elif line.applied_on == '3_global':
                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        return promotion_price

        except Exception as e:
            print("An error occurred:", e)
            return -1.0  # Return a default value in case of an exception or if conditions are not met

        return -1.0

    def sort_points(self, company_id, destinations):

        company = request.env['res.company'].sudo().search([('id', '=', company_id)])

        branche_latitude = company.partner_id.partner_latitude
        branche_longitude = company.partner_id.partner_longitude

        # destinations = req.get('destinations')

        distances = []
        for destination in destinations:
            lat = destination['lat']
            lng = destination['lng']
            distance = self.get_distance(lat, lng, branche_latitude, branche_longitude)
            distances.append((destination, distance))

        # Sort destinations by distance
        sorted_destinations = sorted(distances, key=lambda x: x[1])

        # Now, sorted_destinations contains the points sorted by distance from the origin

        return sorted_destinations

    def get_distance(self, lat, lng, branche_latitude, branche_longitude):
        config = request.env['ir.config_parameter'].sudo()
        APIKey = config.get_param('web_google_maps.google_maps_view_api_key')

        url = f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={lat},{lng}&destinations={branche_latitude},{branche_longitude}&key={APIKey}'

        try:
            response = requests.get(url)
            response_data = json.loads(response.text)

            if response_data.get('status') == 'OK':
                distance = response_data['rows'][0]['elements'][0]['distance']['value'] / 1000
            else:
                distance = -1
        except Exception as e:
            distance = -1

        return distance

    def zone_of_point(self, lat, lng):

        point = {'lat': lat, 'lng': lng}

        companies = request.env['res.company'].sudo().search([])
        companies_zones = []
        for company in companies:
            zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
            zone_list = []
            if zones:
                for zone in zones:
                    zones_coordinates = []
                    lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                    if lat_logs:
                        for lat_log in lat_logs:
                            val_coord = {
                                "lat": lat_log.latitude,
                                "lng": lat_log.longitude
                            }
                            zones_coordinates.append(val_coord)

                    value_coordinate = {
                        "zone_id": zone.id,
                        "coordinates": zones_coordinates
                    }
                    zone_list.append(value_coordinate)

            values = {
                "company_id": company.id,
                "zones": zone_list
            }
            companies_zones.append(values)

        for branch in companies_zones:

            zones = branch['zones']
            company_id = branch['company_id']
            for zone in zones:
                points = zone['coordinates']
                polygon = []

                for point1 in points:
                    polygon.append(point1)

                if self.check_if_point_inside_zone(point, polygon):
                    return zone['zone_id']

        return -1

    def check_if_point_inside_zone(self, point, polygon):
        vertices = polygon
        intersections = 0
        vertices_count = len(vertices)

        for i in range(vertices_count):
            vertex1 = vertices[i]
            vertex2 = vertices[(i + 1) % vertices_count]

            if (
                    vertex1['lat'] == vertex2['lat']
                    and vertex1['lat'] == point['lat']
                    and point['lng'] > min(vertex1['lng'], vertex2['lng'])
                    and point['lng'] < max(vertex1['lng'], vertex2['lng'])
            ):
                # Point is on the edge of the polygon
                return True

            epsilon = 0.00001
            if (
                    abs(self.distance(point, vertex1) + self.distance(point, vertex2) - self.distance(vertex1, vertex2))
                    < epsilon
            ):
                # Point is on the edge of the polygon
                return True

            if (
                    point['lat'] > min(vertex1['lat'], vertex2['lat'])
                    and point['lat'] <= max(vertex1['lat'], vertex2['lat'])
                    and point['lng'] <= max(vertex1['lng'], vertex2['lng'])
                    and vertex1['lat'] != vertex2['lat']
            ):
                xinters = (
                        (point['lat'] - vertex1['lat'])
                        * (vertex2['lng'] - vertex1['lng'])
                        / (vertex2['lat'] - vertex1['lat'])
                        + vertex1['lng']
                )
                if vertex1['lng'] == vertex2['lng'] or point['lng'] <= xinters:
                    intersections += 1

        if intersections % 2 != 0:
            return True
        else:
            return False

        # Define a helper function for distance calculation (you can use your own)

    def distance(self, point1, point2):
        lat1 = math.radians(point1['lat'])
        lng1 = math.radians(point1['lng'])
        lat2 = math.radians(point2['lat'])
        lng2 = math.radians(point2['lng'])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) * math.sin(
            dlng / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return c * 6371000

    def get_company_zones(self, company_id):
        company = request.env['res.company'].sudo().search([('id', '=', company_id)])
        if company:
            zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
            zone_list = []
            if zones:
                for zone in zones:
                    zones_coordinates = []
                    lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                    if lat_logs:
                        for lat_log in lat_logs:
                            val_coord = {
                                "lat": lat_log.latitude,
                                "lng": lat_log.longitude
                            }
                            zones_coordinates.append(val_coord)

                    value_coordinate = {
                        "zone_id": zone.id,
                        "coordinates": zones_coordinates
                    }
                    zone_list.append(value_coordinate)

            values = {
                "company_id": company.id,
                "zones": zone_list
            }


        else:
            values = {

            }
        return values

    def get_company_zones_witout_id(self, company_id=None):
        zone_list = []
        if company_id:
            company = request.env['res.company'].sudo().search([('id', '=', company_id)])
            if company:
                zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
                zone_list = []
                if zones:
                    for zone in zones:
                        zones_coordinates = []
                        lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                        if lat_logs:
                            for lat_log in lat_logs:
                                val_coord = {
                                    "lat": lat_log.latitude,
                                    "lng": lat_log.longitude
                                }
                                zones_coordinates.append(val_coord)

                        value_coordinate = {
                            "coordinates": zones_coordinates
                        }
                        zone_list.append(value_coordinate)

        else:
            companies = request.env['res.company'].sudo().search([])
            if companies:
                for company in companies:
                    zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])

                    if zones:
                        for zone in zones:
                            zones_coordinates = []
                            lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                            if lat_logs:
                                for lat_log in lat_logs:
                                    val_coord = {
                                        "lat": lat_log.latitude,
                                        "lng": lat_log.longitude
                                    }
                                    zones_coordinates.append(val_coord)

                            value_coordinate = {
                                "coordinates": zones_coordinates
                            }
                            zone_list.append(value_coordinate)

        return zone_list

    def zones_without_id(self, company_id=None):

        values = self.get_company_zones_witout_id(company_id)

        return values

    def is_valid_email(self, email):
        # Regular expression pattern for basic email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern, email):
            return True
        else:
            return False

    def calcul_for_address(self, lat, lng, thecompany_id=None, free_delivery=False):

        point = {'lat': lat, 'lng': lng}

        if thecompany_id:
            companies = request.env['res.company'].sudo().search([('id', '=', thecompany_id)])
        else:
            companies = request.env['res.company'].sudo().search([])

        companies_zones = []

        values = None
        for company in companies:
            zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
            zone_list = []

            if zones:

                for zone in zones:
                    zones_coordinates = []
                    lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                    if lat_logs:
                        for lat_log in lat_logs:
                            val_coord = {
                                "lat": lat_log.latitude,
                                "lng": lat_log.longitude
                            }
                            zones_coordinates.append(val_coord)

                    value_coordinate = {
                        "zone_id": zone.id,
                        "coordinates": zones_coordinates
                    }
                    zone_list.append(value_coordinate)

            values_companies = {
                "company_id": company.id,
                "zones": zone_list
            }
            companies_zones.append(values_companies)

        for branch in companies_zones:

            zones = branch['zones']
            company_id = branch['company_id']
            for zone in zones:
                points = zone['coordinates']
                polygon = []

                for point1 in points:
                    polygon.append(point1)

                if self.check_if_point_inside_zone(point, polygon):

                    if free_delivery:
                        fees = 0.0
                        fees_without_TVA = 0.0
                    else:
                        fees = self.get_fees(company_id, zone['zone_id'], point)
                        fees_without_TVA = self.get_fees_without_TVA(fees)
                    if fees == 0:
                        fees = 0.0

                    values = {
                        'zone_id': zone['zone_id'],
                        'company_id': company_id,
                        'fees': fees,
                        'fees_list': self.get_prices_for_currency_list(fees, thecompany_id),
                        'fees_without_TVA': fees_without_TVA,
                        'fees_without_TVA_list': self.get_prices_for_currency_list(fees_without_TVA, thecompany_id)
                    }

        return values

    def get_fees_without_TVA(self, fees):
        delivery_item = request.env['product.template'].sudo().search([('is_delivery', '=', True)], limit=1)
        if delivery_item:
            try:
                taxes = delivery_item.taxes_id
                amount = 0
                for tax in taxes:
                    amount = tax.amount
                fees_without_TVA = round(fees / (1 + amount / 100), 2)
                # res = delivery_item.taxes_id.compute_all(fees/1.15, product=delivery_item)
                # excluded = res['total_excluded']
                # price_product = excluded
            except:
                fees_without_TVA = round(fees, 2)
            return fees_without_TVA
        else:
            return round(fees, 2)

    def get_fees(self, company_id, zone_id, point):
        company = request.env['res.company'].sudo().search([('id', '=', company_id)])

        if company:
            fees_type = company.fees_type
            if fees_type == 'fixed':
                if company.fixed_fees:
                    return round(company.fixed_fees, 2)
                else:
                    return 0.0
            # elif fees_type == 'by_distance':
            #     if company.minimum_fees:
            #         minimum_fees = company.minimum_fees
            #     else:
            #         minimum_fees = 0

            #     if company.price_by_km:
            #         price_by_km = company.price_by_km
            #     else:
            #         price_by_km = 0
            #     the_distance = self.get_distance(point['lat'], point['lng'], company.partner_id.partner_latitude,
            #                                      company.partner_id.partner_longitude)

            #     fees = the_distance * price_by_km
            #     if fees >= minimum_fees:
            #         return fees
            #     else:
            #         return minimum_fees
            else:
                zone = request.env['zone.zone'].sudo().search([('id', '=', zone_id)])
                if zone:
                    if zone.delivery_fees:
                        return round(zone.delivery_fees, 2)
                    else:
                        return 0.0
                else:
                    return 0.0
        else:
            return 0.0

    def get_delivery_time(self, company_id, zone_id):
        company = request.env['res.company'].sudo().search([('id', '=', company_id)])

        if company:
            time_type = company.time_type
            if time_type == 'fixed':
                if company.fixed_time:
                    return company.fixed_time
                else:
                    return 0
            # elif fees_type == 'by_distance':
            #     if company.minimum_fees:
            #         minimum_fees = company.minimum_fees
            #     else:
            #         minimum_fees = 0
            #
            #     if company.price_by_km:
            #         price_by_km = company.price_by_km
            #     else:
            #         price_by_km = 0
            #     the_distance = self.get_distance(point['lat'], point['lng'], company.partner_id.partner_latitude,
            #                                      company.partner_id.partner_longitude)
            #
            #     fees = the_distance * price_by_km
            #     if fees >= minimum_fees:
            #         return fees
            #     else:
            #         return minimum_fees
            else:
                zone = request.env['zone.zone'].sudo().search([('id', '=', zone_id)])
                if zone:
                    if zone.delivery_time:
                        return zone.delivery_time
                    else:
                        return 0
                else:
                    return 0
        else:
            return 0

    def get_product_template_price_json(self, product_template):
        try:
            res = product_template.taxes_id.compute_all(product_template.list_price, product=product_template)
            included = res['total_included']
            price_product = included
        except:
            price_product = product_template.list_price

        price = self.get_product_template_banner_price_json(product_template, price_product)
        if price:
            return price
        else:
            price = self.get_product_template_promotion_price_json(product_template, price_product)
            if price:
                return price
            else:

                price = self.get_product_template_offer_price_json(product_template, price_product)

                if price:
                    return price
                else:
                    value_to_return = {
                        "new_price": price_product,
                        "percent_discount": 0.0
                    }
                    return value_to_return

    def get_product_template_banner_price_json(self, product_template, price_product):

        try:

            published_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_banner', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price
            banner_price = False

            if published_banners:
                for line in published_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)

                        value_to_return = {
                            "new_price": banner_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            banner_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            value_to_return = {
                                "new_price": banner_price,
                                "percent_discount": line.percent_price
                            }
                            return value_to_return

                    elif line.applied_on == '3_global':
                        banner_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)

                        value_to_return = {
                            "new_price": banner_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
        except:
            return False

    def get_product_template_promotion_price_json(self, product_template, price_product):

        try:
            if product_template.company_id:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True),
                     ('company_id', 'in', [product_template.company_id.id, False])])
            else:
                published_promotions = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price

            promotion_price = False

            if published_promotions:
                for line in published_promotions.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:
                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        value_to_return = {
                            "new_price": promotion_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            promotion_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            value_to_return = {
                                "new_price": promotion_price,
                                "percent_discount": line.percent_price
                            }
                            return value_to_return
                    elif line.applied_on == '3_global':

                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        value_to_return = {
                            "new_price": promotion_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
        except:
            return False

    def get_product_template_offer_price_json(self, product_template, price_product):

        try:
            offer_banners = request.env['product.pricelist'].sudo().search(
                [('is_published', '=', True), ('is_offer', '=', True)])

            if price_product:
                shelf_price = price_product  # product_template.list_price
            else:
                shelf_price = product_template.list_price
            offer_price = False

            if offer_banners:
                for line in offer_banners.item_ids:
                    if line.applied_on == '1_product' and line.product_tmpl_id.id == product_template.id:

                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        value_to_return = {
                            "new_price": offer_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
                    elif line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        products_ids = request.env['product.template'].sudo().search(
                            [('categ_id', '=', category_id.id)])
                        if product_template in products_ids:
                            offer_price = shelf_price - (
                                    (line.percent_price / 100) * shelf_price)
                            value_to_return = {
                                "new_price": offer_price,
                                "percent_discount": line.percent_price
                            }
                            return value_to_return
                    elif line.applied_on == '3_global':
                        offer_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                        value_to_return = {
                            "new_price": offer_price,
                            "percent_discount": line.percent_price
                        }
                        return value_to_return
        except:
            return False
