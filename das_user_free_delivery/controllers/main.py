import json
from odoo import http
from odoo.http import request
import requests
from odoo.http import Response
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class DasUserFreeDelivery(http.Controller):

    @http.route(ProductInfo.version + 'user/free-delivery', type='json', auth='public', methods=['Post'], cors="*")
    def get_user_free_delivery(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])

        if user:

            Response.status = '200'
            response = {'status': 200,'response': user.partner_id.free_delivery, 'message': 'OK!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'user Not Found!'}

        return response