import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsValueControllerHttp(http.Controller):

    @http.route('/api/about-us-value-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_value(self):
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
                "image": base_url + "/web/content/" + str(about_us_value.about_us_value_image_attachment.id) if about_us_value.about_us_value_image_attachment.id else "",

                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of About Us Value Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Value Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
