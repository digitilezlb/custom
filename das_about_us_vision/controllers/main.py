import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsVisionController(http.Controller):

    @http.route('/api/about-us-vision', type='json', auth='public', methods=['Post'], cors="*")
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
                about_us_vision = request.env['about.us.vision'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)],limit=1)
            else:
                about_us_vision = request.env['about.us.vision'].with_context(lang='ar_001').sudo().search([],limit=1)
        else:

            if company_id:
                about_us_vision = request.env['about.us.vision'].sudo().search([('company_id', '=', company_id)],limit=1)
            else:
                about_us_vision = request.env['about.us.vision'].sudo().search([],limit=1)
                
       

        if about_us_vision:


            values = {
                "id": about_us_vision.id,
                "name": about_us_vision.name,
                "description": about_us_vision.description,
                "image": "/web/content/" + str(about_us_vision.about_us_vision_image_attachment.id) if about_us_vision.about_us_vision_image_attachment.id else "",

                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Vision Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Vision Found!'}
        return response
