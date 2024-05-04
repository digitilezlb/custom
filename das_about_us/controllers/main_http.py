import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsControllerHttp(http.Controller):

    @http.route('/api/about-us-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_team(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = False
       
            
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


            values = {
                "id": about_us.id,
                "name": about_us.name,
                "description": about_us.description,
                "banner": base_url + "/web/content/" + str(about_us.about_us_banner_attachment.id) if about_us.about_us_banner_attachment.id else "",
                "links": True if about_us.links == 'video' else False,
                "video_url": about_us.video_url if about_us.video_url else "",
                "image_link": base_url + "/web/content/" + str(about_us.image_link_attachment.id) if about_us.image_link_attachment.id else "",
                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Found'}
        else:
            Response.status = '200'
            response = {'status': 200,'response':[], 'message': 'No About Us Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
