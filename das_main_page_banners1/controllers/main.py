from odoo.http import request
from odoo.http import Response
import json
from odoo import http


class MainPageBanner(http.Controller):
    @http.route('/api/main-page-banner1', type='json', auth="public", cors='*', methods=['POST'])
    def get_main_page_banner1(self):

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass

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
                            "image": "/web/content/" + str(
                                banner.banner_image_attachment.id) if banner.banner_image_attachment.id else "",
                        }
                mainpagebanner.append(vals)
            Response.status = '200'
            response = {'status': 200, 'response': mainpagebanner, 'message': 'List Of main page banners1 Found'}
        else:
            Response.status = '200'
            response = {'status': 200, 'message': 'No main page banners1 Found'}
        return response

