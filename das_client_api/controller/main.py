import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re
from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification


class ClientsAPI(http.Controller):
    version = ProductInfo.version

    
        


    @http.route(version + 'client/cancel-order', type='json', auth='public', methods=['Post'], cors="*")
    def cancel_order(self):
        req = json.loads(request.httprequest.data)
        sale_order_id = req.get('order_id')
        user_id = req.get('user_id')
        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if user:
            if sale_order_id:
                sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
                
                if sale_order.partner_id.id == user.partner_id.id:
                    if sale_order.order_status == '2':
                        if sale_order:
                            sale_order.write(
                                {
                                    'state': 'cancel'
                                }
                            )

                            Response.status = '200'
                            response = {'status': 200, 'message': 'Sale Order Canceled!'}
                        else:
                            Response.status = '404'
                            response = {'status': 404, 'message': 'Sale Order Not Found!'}
                    else:
                        Response.status = '404'
                        response = {'status': 404, 'message': 'Can not be deleted!'}
                else:
                    Response.status = '404'
                    response = {'status': 404, 'message': 'Different User!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'Sale Order Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found!'}
        return response
        
    @http.route(ProductInfo.version + 'client/message/send/client', type='json', auth='public', methods=['Post'], cors="*")
    def send_message(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')

        client_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        if client_user:

            images_list = []
            if req.get('images'):
                images_list = req.get('images')

            driver_chat = request.env['driver.chat'].sudo().create({
                "name": req.get('order_id'),
                "message": req.get('message'),
                "image_found": True if len(images_list) > 0 else False,
                "client_user_id": client_user.id
            })
            

            for record in images_list:
                image = request.env['driver.chat.image'].sudo().create({
                    "image": record,
                    "driver_chat_id": driver_chat.id
                })

            Response.status = '200'
            response = {'status': 200, 'message': 'Message Received'}

            try:
                order = request.env['sale.order'].sudo().search([('id', '=', req.get('order_id'))])
                chat = request.env['driver.chat'].sudo().search([('name', '=', req.get('order_id'))], limit=1)

                if chat:
                    driver_user_id = chat.driver_user_id.id

                    if driver_user_id == False:

                        partner = order.driver_id
                        driver_user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)])


                else:

                    partner = order.driver_id
                    driver_user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)])


                if driver_user:
                    notification = Notification
                    message_name = "محادثة واردة"
                    
                    message_description = " محادثة واردة متعلقة بالطلبية رقم " + order.name
    
                    chat_id = '1'
                    notification.send_notification(request.env.user, driver_user, message_name, message_description,
                                                  order.id)

            except:
                pass

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Client Not Found'}
       

        return response

    @http.route(ProductInfo.version + 'message/get-message', type='json', auth='public',
                methods=['Post'], cors="*")
    def get_messages(self):
        req = json.loads(request.httprequest.data)

        order_id = req.get('order_id')
        offset_messages = req.get('offset')
        limit_messages = req.get('limit')
        message_list = []
        user_id = req.get('user_id')
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
                        image_path = "/web/content/" + str(image1.image_attachment.id)
                    else:
                        image_path = ""

                    images.append(image_path)

                if message.client_user_id:
                    client_value = {
                        "name": message.client_user_id.partner_id.name,
                        "image": "/web/content/" + str(
                            message.client_user_id.partner_id.team_member_image_attachment.id) if message.client_user_id.partner_id.team_member_image_attachment.id else "",
                    }
                if message.driver_user_id:
                    driver_value = {
                        "name": message.driver_user_id.partner_id.name,
                        "image": "/web/content/" + str(
                            message.driver_user_id.partner_id.team_member_image_attachment.id) if message.driver_user_id.partner_id.team_member_image_attachment.id else "",
                    }

                create_date_beirut = message.create_date.astimezone(beirut_timezone)
                write_date_beirut = message.write_date.astimezone(beirut_timezone)

                value = {
                    "id": message.id,
                    "conversation_id": message.id,
                    "customer_id": client_value if message.client_user_id else None,
                    "deliveryman_id": driver_value if message.driver_user_id else None,
                    "message": message.message,
                    "attachment": images if len(images) > 0 else None,
                    "created_at": create_date_beirut,
                    "updated_at": write_date_beirut,
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

        return response
        
    @http.route(ProductInfo.version + 'client/track-order-status', type='json', auth='public',
                methods=['Post'], cors="*")
    def track_order_status(self):
        req = json.loads(request.httprequest.data)

        order_id = req.get('order_id')

        user_id = req.get('user_id')
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
                            'image': "/web/content/" + str(
                                order.driver_id.team_member_image_attachment.id) if order.driver_id.team_member_image_attachment.id else ""
                        }
                    else:
                        deliveryman=None
                        
                    values={
                        'order_status': order_status_id,
                        'order_status_id': order_status,
                        'delivery_time': order.delivery_date.astimezone(ProductInfo.beirut_timezone) if order.delivery_date else None,
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

        return response