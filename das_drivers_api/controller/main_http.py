import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re
from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification
import pytz

class DriversAPIHttp(http.Controller):
    version = "/api/"



    @http.route(version + 'order/get-record-location-data-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_record_location_data(self, **res):
        try:
            order_id = int(request.params.get('order_id'))
        except:
            order_id = -1

        order_locations = request.env['driver.order.location.data'].sudo().search([('order_id','=',order_id)],order='create_date desc')
        order_location_list=[]
        if order_locations:

            for order_location in order_locations:
                values={
                    'latitude': order_location.latitude,
                    'longitude': order_location.longitude,
                    'location': order_location.location,
                    'date' : order_location.create_date
                }
                order_location_list.append(values)

            Response.status = '200'
            response = {'status': 200,'response':order_location_list, 'message': 'Locations List Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Location Found!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

        


