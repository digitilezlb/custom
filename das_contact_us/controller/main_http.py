import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class ContactUsControllerHttp(http.Controller):

    @http.route('/api/get-contact-us-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_contact_us(self):

        company_id = False
        contact_us_list =[]
        try:
            company_id = int(request.params.get('company_id'))
            test_company = True
        except:
            company_id = False



        if company_id:
            contact_us = request.env['contact.us'].sudo().search([('company_id', '=', company_id)])
        else:
            contact_us = request.env['contact.us'].sudo().search([])

        if contact_us:
            for contact in contact_us:
                values = {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email if contact.email else "",
                "phone": contact.phone if contact.phone else "",
                "comment": contact.comment if contact.comment else "",
                "company_id": contact.company_id.name if contact.company_id else "",

                 }
                contact_us_list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': contact_us_list, 'message': 'List Of Contact Us Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No About Us Found!'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])


