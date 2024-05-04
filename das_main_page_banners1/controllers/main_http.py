import json
from odoo.http import Response
from odoo import http
from odoo.http import request
import json
from datetime import date, datetime


from odoo.addons.das_publicfunction.controller.main import ProductInfo

class MainPageBannerHttp(http.Controller):
    @http.route('/api/main-page-banner1-http', type='http', auth="public", cors='*', methods=['Get'])
    def get_main_page_banner1(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            company_id = int(request.params.get('company_id'))

        except:
            company_id = False

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        if company_id:
            if lang == "ar":
                banners = request.env['main.banner1'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)])
            else:
                banners = request.env['main.banner1'].sudo().search([('company_id', '=', company_id)])
        else:
            if lang == "ar":
                banners = request.env['main.banner1'].with_context(lang='ar_001').sudo().search([])
            else:
                banners = request.env['main.banner1'].sudo().search([])


        mainpagebanner=[]
        if banners:
            for banner in banners:

                vals = {
                            "name": banner.name if banner.name else "",
                            "description": banner.description if banner.description else "",
                            "url": banner.banner_url if banner.banner_url else "",
                            "image": base_url + "/web/content/" + str(
                                banner.banner_image_attachment.id) if banner.banner_image_attachment.id else "",
                        }
                mainpagebanner.append(vals)
            Response.status = '200'
            response = {'status': 200, 'response': mainpagebanner, 'message': 'List Of main page banners1 Found'}
        else:
            Response.status = '200'
            response = {'status': 200, 'response': [], 'message': 'No main page banners1 Found'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
