import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import time


class AboutUsController(http.Controller):

    @http.route('/api/about-us', type='json', auth='public', methods=['Post'], cors="*")
    def get_team(self):
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass
       
            
        if lang == "ar":
            if company_id:
                about_us = request.env['about.us'].with_context(lang='ar_001').sudo().search([('company_id','=',company_id)],limit=1)
            else:
                about_us = request.env['about.us'].with_context(lang='ar_001').sudo().search([],limit=1)
        else:
            
            if company_id:
                about_us = request.env['about.us'].sudo().search([('company_id','=',company_id)],limit=1)
            else:
                about_us = request.env['about.us'].sudo().search([],limit=1)

        if about_us:

            current_timestamp = time.time()
            values = {
                "id": about_us.id,
                "name": about_us.name,
                "description": about_us.description,
                "banner": "/web/content/" + str(about_us.about_us_banner_attachment.id) if about_us.about_us_banner_attachment.id else "",
                "links": True if about_us.links == 'video' else False,
                "video_url" : about_us.video_url if about_us.video_url else "",
                "image_link" : "/web/content/" + str(about_us.image_link_attachment.id) if about_us.image_link_attachment.id else "",
                # "image_url": "/web/content/" + str(
                #     about_us.image_link_attachment.id) + '?t=' + str(current_timestamp) if about_us.image_link_attachment.id else "",
                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Found!'}
        return response
