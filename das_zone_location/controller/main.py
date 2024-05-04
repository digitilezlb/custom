from odoo import http
from odoo.http import request
from odoo.http import Response
import requests
import json



from odoo.addons.das_publicfunction.controller.main import ProductInfo


class GoogleMaps(http.Controller):

    @http.route(ProductInfo.version + 'zones', type='json', auth='public', methods=['POST'], cors="*")
    def zones(self):

        req = json.loads(request.httprequest.data)

        try:
            thecompany_id = req.get('company_id')
        except:
            thecompany_id = False
            # pass
        if thecompany_id:
            companies = request.env['res.company'].sudo().search([('id','=',thecompany_id)])
        else:
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

        # response = {'status': 404, 'message': 'Zones Not Found!'}
        return response

    @http.route(ProductInfo.version + 'zones/<int:company_id>', type='json', auth='public', methods=['POST'], cors="*")
    def get_company_zones(self, company_id):
        companies = request.env['res.company'].sudo().search([('id', '=', company_id)])

        if companies:
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
                            "zone_id": zone.id,
                            "coordinates": zones_coordinates
                        }
                        zone_list.append(value_coordinate)

                values = {
                    "company_id": company.id,
                    "zones": zone_list
                }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List of Company Zones Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Company Not Found!'}
        return response

    @http.route(ProductInfo.version + '<int:zone_id>/create-zone-coord', type='json', auth='public', methods=['POST'],
                cors="*")
    def create_zone_coord(self, zone_id):
        zone = request.env['zone.zone'].sudo().search([('id', '=', zone_id)])
        zone.remove_geolocation()
        req = json.loads(request.httprequest.data)

        if req.get('coordinates'):

            for rec in req.get('coordinates')[0]:
                values = {
                    'latitude': rec[1],
                    'longitude': rec[0],
                    'zone_id': zone.id
                }
                line = request.env['latitude.longitude'].sudo().create(values)

            zone.get_drawing_map()
        else:
            pass

    @http.route('/get/surveyor/<int:id>/zone', type='json', auth='public', methods=['POST'], cors="*")
    def get_surveyor_zone(self, id):
        data = []
        user_zone = request.env['zone.zone'].sudo().search([('id', '=', id)])
        if user_zone:
            for zone in user_zone:
                for line in zone.geo_id:
                    values = {
                        'id': zone.id,
                        'name': zone.name,
                        'color': zone.marker_color,
                        'latitude': line.latitude,
                        'longitude': line.longitude,
                    }
                    data.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': data, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response

    @http.route('/api/all-zones', type='json', auth='public', methods=['POST'], cors="*")
    def get_all_zone(self):
        data = []
        user_zone = request.env['zone.zone'].sudo().search([])
        if user_zone:
            for zone in user_zone:
                for line in zone.geo_id:
                    values = {
                        'id': zone.id,
                        'name': zone.name,
                        'color': zone.marker_color,
                        'latitude': line.latitude,
                        'longitude': line.longitude,
                    }
                    data.append(values)
            Response.status =   '200'
            response = {'status': 200, 'response': data, 'message': 'Success'}
        else:
            Response.status =   '404'
            response = {'status': 404, 'message': 'No data Found!'}
        return response



    # @http.route('/api/check-if-address-within-zones', type='json', auth='public', methods=['POST'], cors="*")
    # def check_if_address_within_zones(self):
    #     req = json.loads(request.httprequest.data)
    #     point = {'lat': req.get('lat'), 'lng': req.get('lng')}
    #     detail = ProductInfo()
    #     try:
    #         req = json.loads(request.httprequest.data)
    #         thecompany_id = req.get('company_id')
    #     except:
    #         thecompany_id = False
    #         # pass
    #     if thecompany_id:
    #         companies = request.env['res.company'].sudo().search([('id','=',thecompany_id)])
    #     else:
    #         companies = request.env['res.company'].sudo().search([])
            
    #     companies_zones = []
    #     for company in companies:
    #         zones = request.env['zone.zone'].sudo().search([('company_id', '=', company.id)])
    #         zone_list = []
    #         if zones:
    #             for zone in zones:
    #                 zones_coordinates = []
    #                 lat_logs = request.env['latitude.longitude'].sudo().search([('zone_id', '=', zone.id)])
    #                 if lat_logs:
    #                     for lat_log in lat_logs:
    #                         val_coord = {
    #                             "lat": lat_log.latitude,
    #                             "lng": lat_log.longitude
    #                         }
    #                         zones_coordinates.append(val_coord)

    #                 value_coordinate = {
    #                     "zone_id": zone.id,
    #                     "coordinates": zones_coordinates
    #                 }
    #                 zone_list.append(value_coordinate)

    #         values = {
    #             "company_id": company.id,
    #             "zones": zone_list
    #         }
    #         companies_zones.append(values)

    #     for branch in companies_zones:

    #         zones = branch['zones']
    #         company_id = branch['company_id']
    #         for zone in zones:
    #             points = zone['coordinates']
    #             polygon = []

    #             for point1 in points:
    #                 polygon.append(point1)

    #             if detail.check_if_point_inside_zone(point, polygon):
    #                 fees = self.get_fees(company_id, zone['zone_id'], point)
    #                 values = {
    #                     'zone_id': zone['zone_id'],
    #                     'company_id': company_id,
    #                     'fees': fees,
    #                     'fees_without_TVA': self.get_fees_without_TVA(fees)
    #                 }

    #                 Response.status = '200'
    #                 response = {'status': 200, 'response': values, 'message': 'Success'}
    #                 return response

    #     Response.status = '404'
    #     response = {'status': 404, 'message': 'Out Of Zones!'}
    #     return response

    # def get_fees_without_TVA(self,fees):
    #     delivery_item = request.env['product.template'].sudo().search([('is_delivery','=',True)],limit=1)
    #     if delivery_item:
    #         try:
    #             taxes = delivery_item.taxes_id
    #             amount = 0
    #             for tax in taxes:
    #                 amount = tax.amount
    #             fees_without_TVA = round(fees/ (1+ amount/100),2)
    #             # res = delivery_item.taxes_id.compute_all(fees/1.15, product=delivery_item)
    #             # excluded = res['total_excluded']
    #             # price_product = excluded
    #         except:
    #             fees_without_TVA = fees
    #         return  fees_without_TVA
    # def get_fees(self, company_id, zone_id, point):
    #     company = request.env['res.company'].sudo().search([('id', '=', company_id)])
    #     detail = ProductInfo()
    #     if company:
    #         fees_type = company.fees_type
    #         if fees_type == 'fixed':
    #             if company.fixed_fees:
    #                 return company.fixed_fees
    #             else:
    #                 return 0
    #         elif fees_type == 'by_distance':
    #             if company.minimum_fees:
    #                 minimum_fees = company.minimum_fees
    #             else:
    #                 minimum_fees = 0

    #             if company.price_by_km:
    #                 price_by_km = company.price_by_km
    #             else:
    #                 price_by_km = 0
    #             the_distance = detail.get_distance(point['lat'], point['lng'], company.partner_id.partner_latitude,
    #                                              company.partner_id.partner_longitude)

    #             fees = the_distance * price_by_km
    #             if fees >= minimum_fees:
    #                 return fees
    #             else:
    #                 return minimum_fees
    #         else:
    #             zone = request.env['zone.zone'].sudo().search([('id', '=', zone_id)])
    #             if zone:
    #                 if zone.delivery_fees:
    #                     return zone.delivery_fees
    #                 else:
    #                     return 0
    #             else:
    #                 return 0
    #     else:
    #         return 0
    
    @http.route('/api/check-if-address-within-zones', type='json', auth='public', methods=['POST'], cors="*")
    def check_if_address_within_zones(self):
        req = json.loads(request.httprequest.data)
        # point = {'lat': req.get('lat'), 'lng': req.get('lng')}
        detail = ProductInfo()

        try:
            thecompany_id = req.get('company_id')
        except:
            thecompany_id = False
            # pass
        try:
            user_id = req.get('user_id')
        except:
            user_id = -1

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        try:
            free_delivery = retailer_user.partner_id.free_delivery
        except:
            free_delivery = False

        values = detail.calcul_for_address(req.get('lat'),req.get('lng'),thecompany_id,free_delivery)
        if values:
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Out Of Zones!'}
        return response

    @http.route('/api/sort-points', type='json', auth='public', methods=['POST'], cors="*")
    def sort_points(self):
        req = json.loads(request.httprequest.data)
        company_id = req.get('company_id')
        company = request.env['res.company'].sudo().search([('id', '=', company_id)])

        branche_latitude = company.partner_id.partner_latitude
        branche_longitude = company.partner_id.partner_longitude

        destinations = req.get('destinations')
        detail  = ProductInfo()
        distances = []
        for destination in destinations:
            lat = destination['lat']
            lng = destination['lng']
            distance = detail.get_distance(lat, lng, branche_latitude, branche_longitude)
            distances.append((destination, distance))

        # Sort destinations by distance
        sorted_destinations = sorted(distances, key=lambda x: x[1])

        # Now, sorted_destinations contains the points sorted by distance from the origin
        # print(sorted_destinations)



