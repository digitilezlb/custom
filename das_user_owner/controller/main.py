import json
from odoo.http import Response
from odoo import http, exceptions
from odoo.http import request
from werkzeug.wrappers import Response as REEEsp
import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
import hashlib
from datetime import datetime
from odoo.addons.das_publicfunction.controller.main import ProductInfo


class DasUserOwner(http.Controller):
    version = ProductInfo.version


    @http.route(version + 'make-user-owner', type='json', auth='public', methods=['Post'], cors="*")
    def make_user_owner(self):
        # 204
        req = json.loads(request.httprequest.data)

        user_id = req.get('user_id')


        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if user:

            user.sudo().write({'user_owner': True})

            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
        return response
