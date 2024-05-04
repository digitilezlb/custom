from odoo.http import request
from odoo.http import Response
import json
from odoo import http
import odoo
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class FirstOrderDiscount(http.Controller):
    version = ProductInfo.version
    @http.route( '/api/first-order-discount', type='json', auth="public", cors='*', methods=['POST'])
    def get_first_order_discount(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        if user:
            vals = self.get_first_order_discount_local(user)
            Response.status = '200'
            response = {'status': 200, 'response': vals, 'message': 'user first order discount'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
        return response


    def get_first_order_discount_local(self,user):
        sale = request.env['sale.order'].sudo().search([('partner_id', '=', user.partner_id.id)])
        first_order_discount = request.env['website.first.order'].sudo().search([('id', '=', 1)])
        if not sale:
            first_order = True
            if first_order_discount.discount_type == '1':
                discount_val = first_order_discount.amount_discount
                discount_type = "Discount"
                discount_type_id = "1"
                active = first_order_discount.enable
            # elif first_order_discount.discount_type == '2':
            #     discount_val = first_order_discount.amount_discount
            #     discount_type = "Amount"
            #     discount_type_id = "2"
            elif first_order_discount.discount_type == '2':
                discount_val = 0.0
                discount_type = "Free delivery"
                discount_type_id = "2"
                active = first_order_discount.enable
            else:
                discount_val = 0.0
                discount_type = 'None'
                discount_type_id = "0"
                active = False
        else:
            first_order = False
            discount_val = 0.0
            discount_type = 'None'
            discount_type_id = "0"
            active = False
        vals = {
            "active":active,
            "first_order": first_order,
            "discount_type_id": discount_type_id,
            "discount_type": discount_type,
            "discount_val": discount_val
        }
        return vals