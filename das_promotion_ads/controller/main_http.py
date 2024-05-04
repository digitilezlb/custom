import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import json
from odoo.addons.das_publicfunction.controller.main import ProductInfo


class PromotionAdsHttp(http.Controller):

    @http.route('/api/promotions-http', type='http', auth='public', methods=['Get'], cors="*")
    def promotions_information(self):
        x_localization = request.httprequest.headers.get('x-localization')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        lang = "en"

        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = False

        if company_id:
            if lang == "ar":
                published_ads = request.env['product.pricelist'].with_context(lang='ar_001').sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True),
                     ('company_id', 'in', [company_id, False])])

            else:
                published_ads = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True),
                     ('company_id', 'in', [company_id, False])])
        else:
            if lang == "ar":
                published_ads = request.env['product.pricelist'].with_context(lang='ar_001').sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True)])

            else:
                published_ads = request.env['product.pricelist'].sudo().search(
                    [('is_published', '=', True), ('is_promotion', '=', True)])

        ads_list = []
        product_list = []

        try:
            user_id = int(request.params.get('company_id'))
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
        if published_ads:
            for ad in published_ads:
                product_list = []
                for line in ad.item_ids:

                    is_fav = False
                    if line.applied_on == '1_product':
                        if line.product_tmpl_id.app_publish == True:

                            old_price = line.product_tmpl_id.list_price
                            new_price = old_price - (
                                    (line.percent_price / 100) * old_price)
                            if all_wishlist:
                                for wish in all_wishlist:
                                    if line.product_tmpl_id.id == wish.product_template_id.id:
                                        is_fav = True
                                        break

                            if lang == "ar":
                                thetemplate = request.env['product.template'].with_context(
                                    lang='ar_001').sudo().search(
                                    [('id', '=', line.product_tmpl_id.id)])

                            else:
                                thetemplate = request.env['product.template'].sudo().search(
                                    [('id', '=', line.product_tmpl_id.id)])

                            try:
                                res = thetemplate.taxes_id.compute_all(thetemplate.list_price, product=thetemplate)
                                included = res['total_included']
                                price_product = included
                            except:
                                price_product = thetemplate.list_price

                            product_template_price_json = Product_Info.get_product_template_price_json(thetemplate)

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

                            product_list.append({"product_tmpl_id": line.product_tmpl_id.id,
                                                 "product_id": line.product_tmpl_id.id,
                                                 "product_name": thetemplate.name,
                                                 "product_image": base_url +  "/web/content/" + str(
                                                     line.product_tmpl_id.image_attachment.id) if line.product_tmpl_id.image_attachment.id else "",
                                                 "price": line.product_tmpl_id.list_price,
                                                 "price_list": Product_Info.get_prices_for_currency_list(
                                                     line.product_tmpl_id.list_price, company_id),
                                                 'template_sale_price_new': new_price,
                                                 'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                                                     new_price, company_id),
                                                 'template_sale_price_old': round(price_product, 2),
                                                 'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                                                     price_product, company_id),
                                                 'percent_discount': percent_discount,
                                                 'is_fav': is_fav,
                                                 })
                    if line.applied_on == '2_product_category':
                        category_id = request.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                        if lang == "ar":
                            products_ids = request.env['product.template'].with_context(
                                lang='ar_001').sudo().search(
                                [('categ_id', '=', category_id.id), ('app_publish', '=', True)])
                        else:
                            products_ids = request.env['product.template'].sudo().search(
                                [('categ_id', '=', category_id.id), ('app_publish', '=', True)])
                        for product in products_ids:
                            old_price = product.list_price
                            new_price = old_price - (
                                    (line.percent_price / 100) * old_price)
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

                            product_list.append({"product_tmpl_id": product.id,
                                                 "product_id": product.id,
                                                 "product_name": product.name,
                                                 "product_image": base_url + "/web/content/" + str(
                                                     product.image_attachment.id) if product.image_attachment.id else "",
                                                 "price": product.list_price,
                                                 "price_list": Product_Info.get_prices_for_currency_list(
                                                     product.list_price, company_id),
                                                 'template_sale_price_new': new_price,
                                                 'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                                                     new_price, company_id),
                                                 'template_sale_price_old': round(price_product, 2),
                                                 'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                                                     price_product, company_id),
                                                 'percent_discount': percent_discount,
                                                 'is_fav': is_fav,
                                                 })
                    if line.applied_on == '3_global':

                        if lang == "ar":
                            products_ids = request.env['product.template'].with_context(
                                lang='ar_001').sudo().search([('app_publish', '=', True)])
                        else:
                            products_ids = request.env['product.template'].sudo().search([('app_publish', '=', True)])

                        for product in products_ids:
                            old_price = product.list_price
                            new_price = old_price - (
                                    (line.percent_price / 100) * old_price)

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

                            product_list.append({"product_tmpl_id": product.id,
                                                 "product_id": product.id,
                                                 "product_name": product.name,
                                                 "product_image": base_url + "/web/content/" + str(
                                                     product.image_attachment.id) if product.image_attachment.id else "",
                                                 "price": product.list_price,
                                                 "price_list": Product_Info.get_prices_for_currency_list(
                                                     product.list_price, company_id),
                                                 'template_sale_price_new': new_price,
                                                 'template_sale_price_new_list': Product_Info.get_prices_for_currency_list(
                                                     new_price, company_id),
                                                 'template_sale_price_old': round(price_product, 2),
                                                 'template_sale_price_old_list': Product_Info.get_prices_for_currency_list(
                                                     price_product, company_id),
                                                 'percent_discount': percent_discount,
                                                 'is_fav': is_fav,
                                                 })
                values = {
                    "promotion_id": ad.id,
                    "promotion_name": ad.name,
                    "promotion_image": base_url + "/web/content/" + str(ad.image_attachment.id) if ad.image_attachment.id else "",
                    "product_ids": product_list,
                }
                ads_list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': ads_list, 'message': 'List Of Promotions Found'}
        else:
            Response.status = '200'
            response = {'status': 200,'response': [], 'message': 'No Products Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])


