from odoo.http import request
from odoo.http import Response
import json
from odoo import http
import odoo


class FAQ(http.Controller):
    @http.route('/api/faqs', type='json', auth="public", cors='*', methods=['POST'])
    def get_list_of_faq_public_http(self):
        req = json.loads(request.httprequest.data)
        company_id = req.get('company_id')
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        if company_id:
            if lang == "ar":
                faq = request.env['website.faq'].with_context(lang='ar_001').sudo().search([('company_id', '=', company_id)])
            else:
                faq = request.env['website.faq'].sudo().search([('company_id','=',company_id)])
        else:
            if lang == "ar":
                faq = request.env['website.faq'].with_context(lang='ar_001').sudo().search([])
            else:
                faq = request.env['website.faq'].sudo().search([])
        # faq = request.env['website.faq'].sudo().search([])
        list = []
        if faq:
            for f in faq:
                if f:
                    values = {
                        "question": f.name,
                        "answer": f.answer,
                        "banner": "/web/content/" + str(f.banner_attachment.id) if f.banner_attachment.id else ""
                    }
                    list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': list, 'message': 'list of FAQ'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no FAQ found'}
        return response

