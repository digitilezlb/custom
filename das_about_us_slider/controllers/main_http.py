import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class AboutUsSliderControllerHttp(http.Controller):

    @http.route('/api/about-us-slider-http', type='http', auth='public', methods=['Get'], cors="*")
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
                about_us_sliders = request.env['about.us.slider'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)])
            else:
                about_us_sliders = request.env['about.us.slider'].with_context(lang='ar_001').sudo().search([])
        else:

            if company_id:
                about_us_sliders = request.env['about.us.slider'].sudo().search([('company_id', '=', company_id)])
            else:
                about_us_sliders = request.env['about.us.slider'].sudo().search([])
        

        sliders = []
        if about_us_sliders:
            for slider in about_us_sliders:

                values = {
                    "id": slider.id,
                    "name": slider.name,
                    "image": base_url + "/web/content/" + str(slider.about_us_slider_image_attachment.id) if slider.about_us_slider_image_attachment.id else "",

                    }
                sliders.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': sliders, 'message': 'List Of About Us Sliders Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Slider Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
