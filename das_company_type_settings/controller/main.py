from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
import requests
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class CompanyTypeSettings(http.Controller):
     @http.route(ProductInfo.version + 'company-type-settings', type='json', auth='public', methods=['Post'], cors="*")
     def get_company_type_settings(self):

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
            if company_id:
               restaurant = request.env['res.company'].sudo().search([('id', '=', company_id)])
            else:
               restaurant = request.env['res.company'].sudo().search([],order='id',limit=1)
        except:
            restaurant = request.env['res.company'].sudo().search([],order='id',limit=1)

        if restaurant:
            values = {
                "has_delivery": restaurant.has_delivery,
                "has_pickup": restaurant.has_pickup,

            }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Company Type Settings Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no data found'}
        return response