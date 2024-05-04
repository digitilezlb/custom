from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
from datetime import date, datetime, timedelta
import requests
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class CompanyInfo(http.Controller):
   

    @http.route(ProductInfo.version + 'legal-information', type='json', auth='public', methods=['Post'], cors="*")
    def get_legal_information(self):
        # restaurant = request.env['res.company'].sudo().search([('id', '=', request.env.user.company_id.id)])

        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
            if company_id:
                if lang == "ar":
                    restaurant = request.env['res.company'].with_context(lang='ar_001').sudo().search([('id', '=', company_id)])
                else:
                    restaurant = request.env['res.company'].sudo().search([('id', '=', company_id)])
            else:
                if lang == "ar":
                    restaurant = request.env['res.company'].with_context(lang='ar_001').sudo().search([], order='id', limit=1)
                else:
                    restaurant = request.env['res.company'].sudo().search([],order='id',limit=1)
        except:
            if lang == "ar":
                restaurant = request.env['res.company'].with_context(lang='ar_001').sudo().search([], order='id', limit=1)
            else:
                restaurant = request.env['res.company'].sudo().search([],order='id',limit=1)

        if restaurant:
            values = {
                # "about_us": restaurant.about_us,
                "terms_and_conditions": restaurant.terms_and_conditions if restaurant.terms_and_conditions else "",
                "terms_and_conditions_url": restaurant.terms_and_conditions_url if restaurant.terms_and_conditions_url else "",
                "privacy_policy": restaurant.privacy_policy if restaurant.privacy_policy else "",
                "privacy_policy_url": restaurant.privacy_policy_url if restaurant.privacy_policy_url else "",
                "support": restaurant.support if restaurant.support else ""
            }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Legal Information Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no data found'}
        return response
        
    @http.route(ProductInfo.version + 'branches', type='json', auth='public', methods=['Post'], cors="*")
    def get_branches_information(self):
        # restaurant = request.env['res.company'].sudo().search([('id', '=', request.env.user.company_id.id)])

        branches = request.env['res.company'].sudo().search([])
        branch_list = []
        if branches:
            for branch in branches:
                values = {
                    "id":branch.id,
                    "name":branch.name
                }
                branch_list.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': branch_list, 'message': 'Branches Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'no branch found'}
        return response

