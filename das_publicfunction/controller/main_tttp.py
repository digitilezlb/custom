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
from  odoo.addons.das_publicfunction.controller.main import ProductInfo

class ProductInfoHttp(http.Controller):


    @http.route(ProductInfo.version + 'config-http/<int:company_id>', type='http', auth='public', methods=['Get'] ,cors='*')
    def get_settings(self,company_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        detail = ProductInfo()
        try:
            # req = json.loads(request.httprequest.data)
            # company_id = req.get('company_id')
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
                                "opening_time": detail.format_time_from_float(att.hour_from),
                                "closing_time": detail.format_time_from_float(att.hour_to)
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
                    category_image_attachment = base_url + "/web/content/" + str(restaurant_name.category_image_attachment.id)
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
                    cart_image_attachment = base_url + "/web/content/" + str(
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
                    checkout_image_attachment = base_url + "/web/content/" + str(
                        restaurant_name.checkout_image_attachment.id)
                else:
                    checkout_image_attachment = ''



            except:
                checkout_title = ""
                checkout_image_attachment = ""

            try:
                if restaurant_name.faq_banner_attachment.id:
                    faq_banner = base_url + "/web/content/" + str(
                        restaurant_name.faq_banner_attachment.id)
                else:
                    faq_banner = ''

            except:
                faq_banner = ""

            try:
                if restaurant_name.career_banner_attachment.id:
                    career_banner = base_url + "/web/content/" + str(
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
                    deal_banner = base_url + "/web/content/" + str(
                    restaurant_name.deal_banner_image_attachment.id)
                else:
                    deal_banner = ''

                if restaurant_name.deal_background_image_attachment.id:
                    deal_background = base_url + "/web/content/" + str(
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
                    promotion_banner = base_url + "/web/content/" + str(
                        restaurant_name.promotion_image_attachment.id)
                else:
                    promotion_banner = ''

                if restaurant_name.footer_image_attachment.id:
                    footer_banner = base_url + "/web/content/" + str(
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
                    restaurant_favicon = base_url +"/web/content/" + str(restaurant_name.favicon_attachment.id)
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
                    restaurant_loader_for_web_app = base_url +"/web/content/" + str(restaurant_name.loader_image_attachment.id)
                else:
                    restaurant_loader_for_web_app = ""

                if restaurant_name.splash_image_attachment.id:
                    splash_background_for_mobile_app = base_url + "/web/content/" + str(restaurant_name.splash_image_attachment.id)
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
                "company_id": restaurant_name.id,
                "restaurant_name": restaurant_name.name if restaurant_name.name else "",
                "restaurant_name_arabic": restaurant_name_arabic,
                "restaurant_address": address,
                "restaurant_address_arabic": restaurant_address_arabic,
                "restaurant_phone": restaurant_name.phone if restaurant_name.phone else '',
                "restaurant_email": restaurant_name.email if restaurant_name.email else '',
                "currency_symbol": restaurant_name.currency_id.name,
                "currency_symbol_en": restaurant_name.currency_id.name,
                "currency_id": restaurant_name.currency_id.id,
                "currency_list": currency_list,
                "restaurant_logo": base_url + "/web/content/" + str(
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
            Response.status = '200'
            response = {'status': 200,'response': [], 'message': 'No data Found!'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])




