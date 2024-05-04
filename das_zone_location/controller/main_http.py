from odoo import http
from odoo.http import request
from odoo.http import Response
import requests
import json



from odoo.addons.das_publicfunction.controller.main import ProductInfo


class GoogleMapsHttp(http.Controller):

    @http.route(ProductInfo.version + 'zones-http', type='http', auth='public', methods=['Get'], cors="*")
    def zones(self):
        companies = request.env['res.company'].sudo().search([])
        companies_zones = []
        for company in companies:
            zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
            zone_list = []
            if zones:
                for zone in zones:
                    zones_coordinates = []
                    lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
                    if lat_logs:
                        for lat_log in lat_logs:
                            val_coord = {
                                "lat": lat_log.latitude,
                                "lng": lat_log.longitude
                            }
                            zones_coordinates.append(val_coord)

                    value_coordinate = {
                        "coordinates": zones_coordinates
                    }
                    zone_list.append(value_coordinate)

            values = {
                "company_id": company.id,
                "zones": zone_list
            }
            companies_zones.append(values)

        Response.status = '200'
        response = {'status': 200, 'response': companies_zones, 'message': 'List of Zones Found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route('/api/check-if-address-within-zones-http', type='http', auth='public', methods=['Get'], cors="*")
    def check_if_address_within_zones(self):

        # point = {'lat': req.get('lat'), 'lng': req.get('lng')}
        detail = ProductInfo()

        try:
            thecompany_id = int(request.params.get('company_id'))
        except:
            thecompany_id = -1



        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        try:
            lng = float(request.params.get('lng'))
        except:
            lng = -1.0

        try:
            lat = float(request.params.get('lat'))
        except:
            lat = -1.0

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        try:
            free_delivery = retailer_user.partner_id.free_delivery
        except:
            free_delivery = False

        values = detail.calcul_for_address(lat, lng, thecompany_id, free_delivery)
        if values:
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Out Of Zones!'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])