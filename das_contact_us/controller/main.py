import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class ContactUsController(http.Controller):

    @http.route('/api/get-contact-us', type='json', auth='public', methods=['Post'], cors="*")
    def get_contact_us(self):

        company_id = False
        contact_us_list =[]

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass

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

        return response

    @http.route('/api/contact-us', type='json', auth='public', methods=['Post'], cors="*")
    def save_contact_us(self):
        try:
            req = json.loads(request.httprequest.data)
            # name = req.get('name')
            # email = req.get('email')
            # phone = req.get('phone')
            # comment = req.get('comment')
            # company_id = req.get('company_id')
            
            detail = ProductInfo()
            if detail.is_valid_email(req.get('email'))==False:
                Response.status = '404'
                response = {'status': 404, 'message': 'email not valid!!'}
                return response
                
            contact_us = request.env['contact.us'].sudo().create({
                "name": req.get('name'),
                "email": req.get('email'),
                "phone": req.get('phone'),
                "comment": req.get('comment'),
                "company_id": req.get('company_id'),

            })
            Response.status = '200'
            response = {'status': 200, 'message': 'Contact Us Received'}
        except:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}

        return response