import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class DriverController(http.Controller):
    @http.route('/api/confirm-deliverywww', type='json', auth='public', methods=['Post'], cors="*")
    def confirm_delivery(self):

        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('sale_order_id')
        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().search([('id','=',sale_order_id)])
            if sale_order:
                sale_order.write(
                    {'order_status': "7"}
                )

                order_trip = request.env['orders.trip'].sudo().search([('order_ids','in',sale_order.id)])
                if order_trip:
                    is_delivered = True
                    for inv in order_trip.order_ids:
                        if inv.order_status != '7':
                            is_delivered  = False
                    if is_delivered:
                        order_trip.write(
                                {'state': 'arrived'}
                            )
                Response.status = '200'
                response = {'status': 200, 'message': 'Sale Order Delivered!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Sale Order Not Found!'}


        return response