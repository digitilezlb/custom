import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsMissionControllerHttp(http.Controller):

    @http.route('/api/about-us-mission-http', type='http', auth='public', methods=['Get'], cors="*")
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
                about_us_mission = request.env['about.us.mission'].with_context(lang='ar_001').sudo().search([('company_id','=',company_id)],limit=1)
            else:
                about_us_mission = request.env['about.us.mission'].with_context(lang='ar_001').sudo().search([],limit=1)
        else:
            
            if company_id:
                about_us_mission = request.env['about.us.mission'].sudo().search([('company_id','=',company_id)],limit=1)
            else:
                about_us_mission = request.env['about.us.mission'].sudo().search([],limit=1)
                
        

        if about_us_mission:


            values = {
                "id": about_us_mission.id,
                "name": about_us_mission.name,
                "description": about_us_mission.description,
                "image": base_url + "/web/content/" + str(about_us_mission.about_us_mission_image_attachment.id) if about_us_mission.about_us_mission_image_attachment.id else "",

                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Mission Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Mission Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
