import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re

from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification


class ClientsAPIHttp(http.Controller):
    version = ProductInfo.version


    @http.route(ProductInfo.version + 'message/get-message-http', type='http', auth='public',
                methods=['Get'], cors="*")
    def get_messages(self):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            order_id = int(request.params.get('order_id'))
        except:
            order_id = -1

        try:
            offset_messages = int(request.params.get('offset'))
        except:
            offset_messages = -1

        try:
            limit_messages = int(request.params.get('limit'))
        except:
            limit_messages = -1

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        message_list = []

        client_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if client_user:
            messages = request.env['driver.chat'].sudo().search([('name', '=', order_id)], order='create_date Desc',
                                                                limit=limit_messages,
                                                                offset=offset_messages * limit_messages)
            # leads = CrmLead.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
            total_size = len(messages)
            beirut_timezone = ProductInfo.beirut_timezone
            for message in messages:
                images = []
                for image1 in message.images:
                    if image1.image_attachment.id:
                        image_path = base_url + "/web/content/" + str(image1.image_attachment.id)
                    else:
                        image_path = ""
                    images.append(image_path)

                if message.client_user_id:
                    client_value = {
                        "name": message.client_user_id.partner_id.name,
                        "image": base_url + "/web/content/" + str(
                            message.client_user_id.partner_id.team_member_image_attachment.id) if message.client_user_id.partner_id.team_member_image_attachment.id else "",
                    }
                if message.driver_user_id:
                    driver_value = {
                        "name": message.driver_user_id.partner_id.name,
                        "image": base_url + "/web/content/" + str(
                            message.driver_user_id.partner_id.team_member_image_attachment.id) if message.driver_user_id.partner_id.team_member_image_attachment.id else "",
                    }
                try:
                    create_date_beirut = message.create_date.astimezone(beirut_timezone)
                    write_date_beirut = message.write_date.astimezone(beirut_timezone)

                    create_date_beirut_datetime = create_date_beirut.strftime('%Y-%m-%d %H:%M:%S')
                    write_date_beirut_datetime = write_date_beirut.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    create_date_beirut_datetime = ""
                    write_date_beirut_datetime = ""

                value = {
                    "id": message.id,
                    "conversation_id": message.id,
                    "customer_id": client_value if message.client_user_id else None,
                    "deliveryman_id": driver_value if message.driver_user_id else None,
                    "message": message.message,
                    "attachment": images if len(images) > 0 else None,
                    "created_at": create_date_beirut_datetime,
                    "updated_at": write_date_beirut_datetime,
                }
                message_list.append(value)

            values = {
                "total_size": total_size,
                "limit": limit_messages,
                "offset": offset_messages,
                "messages": message_list

            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List of Messages'}


        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'client Not Found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
        
    @http.route(ProductInfo.version + 'client/track-order-status-http', type='http', auth='public',
                methods=['Get'], cors="*")
    def track_order_status(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        try:
            order_id = int(request.params.get('order_id'))
        except:
            order_id = -1


        client_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if client_user:
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            order_location = request.env['driver.order.location.data'].sudo().search([('order_id', '=', order_id)])

            if order_location:

                if len(order_location)>0:

                    saved_location = True
                else:
                    saved_location = False
            else:
                saved_location = False
                
            if order:
                if order.partner_id.id == client_user.partner_id.id:
                    order_status = order.order_status
                    if order_status == "2":
                        order_status_id = "Draft"
                    elif order_status == "3":
                        order_status_id = "Confirmed"
                    elif order_status == "4":
                        order_status_id = "In Progress"
                    elif order_status == "5":
                        order_status_id = "Ready"
                    elif order_status == "6":
                        order_status_id = "Out For Delivery"
                    elif order_status == "7":
                        order_status_id = "Delivered"
                
                    if saved_location==False:
                        if order_status =='5' or order_status =='6':
                            order_status='4'
                            order_status_id = "In Progress"
                    # deliveryman = {}
                    if order.driver_id:
                        deliveryman = {
                            'id': order.driver_id.id,
                            'name': order.driver_id.name,
                            'phone': order.driver_id.mobile if order.driver_id.mobile else "",
                            'email': order.driver_id.email if order.driver_id.email else "",
                            'image': base_url + "/web/content/" + str(
                                order.driver_id.team_member_image_attachment.id) if order.driver_id.team_member_image_attachment.id else ""
                        }
                    else:
                        deliveryman=None
                    try:
                        order_date = order.delivery_date.astimezone(ProductInfo.beirut_timezone)
                        order_datetime = order_date.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        order_datetime = ""
                    values={
                        'order_status': order_status_id,
                        'order_status_id': order_status,
                        'delivery_time': order_datetime,
                        'deliveryman': deliveryman,
                        'restaurant_location':{
                            'lat':  order.company_id.partner_id.partner_latitude if order.company_id.partner_id.partner_latitude else 0,
                            "lng": order.company_id.partner_id.partner_longitude if order.company_id.partner_id.partner_longitude else 0,
                        },
                        'client_location': {
                            'lat': order.partner_shipping_id.partner_latitude if order.partner_shipping_id.partner_latitude else 0,
                            "lng": order.partner_shipping_id.partner_longitude if order.partner_shipping_id.partner_longitude else 0,
                        },
                    }
                    Response.status = '200'
                    response = {'status': 200, 'response':values , 'message': 'List of Messages'}
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Different User!'}
            else:
                Response.status = '404'
                response = {'status': 404,   'message': 'Order Not Found!'}



        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'client Not Found'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])