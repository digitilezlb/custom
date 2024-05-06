import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsValueController(http.Controller):

    @http.route('/api/about-us-value', type='json', auth='public', methods=['Post'], cors="*")
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
                about_us_value = request.env['about.us.value'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)],limit=1)
            else:
                about_us_value = request.env['about.us.value'].with_context(lang='ar_001').sudo().search([],limit=1)
        else:

            if company_id:
                about_us_value = request.env['about.us.value'].sudo().search([('company_id', '=', company_id)],limit=1)
            else:
                about_us_value = request.env['about.us.value'].sudo().search([],limit=1)
                
                
        

        if about_us_value:


            values = {
                "id": about_us_value.id,
                "name": about_us_value.name,
                "description": about_us_value.description,
                "image": "/web/content/" + str(about_us_value.about_us_value_image_attachment.id) if about_us_value.about_us_value_image_attachment.id else "",

                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Value Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Value Found!'}
        return response
