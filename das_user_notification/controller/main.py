import json
from odoo import http
from odoo.http import request
import requests
from odoo.http import Response
from odoo.addons.das_publicfunction.controller.main import ProductInfo


class Notification(http.Controller):

    @http.route([ProductInfo.version + 'delivery-man/update-fcm-token', ProductInfo.version + 'branch/update-fcm-token',
                 ProductInfo.version + 'kitchen/update-fcm-token'], type='json', auth='user', methods=['Post'],
                cors="*")
    def update_user_token(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        Response.status = '200'
        # response = {'status': 200, 'message': 'fcm token updated!'}

        fcm_token = req.get('fcm_token')
        if user:
            if self.update_token(user, fcm_token):
                Response.status = '200'
                response = {'status': 200, 'message': 'fcm token updated!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'fcm token  Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'user Not Found!'}

        return response

    @http.route(ProductInfo.version + 'user/update-fcm-token', type='json', auth='public', methods=['Post'], cors="*")
    def update_user_token_user(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])

        Response.status = '200'
        response = {'status': 200, 'message': 'fcm token updated!'}

        fcm_token = req.get('fcm_token')
        if user:
            if self.update_token(user, fcm_token):
                Response.status = '200'
                response = {'status': 200, 'message': 'fcm token updated!'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'fcm token  Not Found!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'user Not Found!'}

        return response

    def update_token(self, user, fcm_token):

        if user:
            if fcm_token:
                user.write(
                    {'user_token': fcm_token}
                )
                return True

            else:
                return False
        else:
            return False

    @http.route('/api/platforms', type='json', auth='user', methods=['Post'])
    def get_platforms(self):
        platforms = request.env['mobile.platform'].sudo().search([])
        platforms_list = []
        if platforms:
            for plat in platforms:
                platforms_list.append({
                    "platform_id": plat.id,
                    "platform_name": plat.name
                })
            Response.status = '200'
            response = {'status': 200, 'response': platforms_list, 'message': 'list of platforms Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No platform Found!'}
        return response

    @http.route('/api/notification-post', type='json', auth='user', methods=['POST'])
    def notification(self):
        req = json.loads(request.httprequest.data)
        user_id = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        values = {
            'user_token': req.get('token'),
            'user_platform': req.get('platform'),
        }
        notification = user_id.sudo().write(values)
        if notification:
            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}
        return response

    @http.route('/api/notifications', type='json', auth='user', methods=['Post'])
    def get_notification(self):
        all_notif = request.env['sent.notification'].sudo().search([])
        user_notif = []
        for notif in all_notif:
            for user in notif.users:
                if user.id == request.env.uid:
                    type_id = 0
                    model_id = 0
                    if notif.notif_type == "announcement_1":
                        type_id = 1
                        model_id = 0
                    elif notif.notif_type == "promotion_2":
                        type_id = 2
                        model_id = notif.promo_id.id
                    elif notif.notif_type == "ad_3":
                        type_id = 3
                        model_id = notif.promo_id.id
                    elif notif.notif_type == "deal_4":
                        type_id = 4
                        model_id = notif.promo_id.id
                    elif notif.notif_type == "trip_assigned_5":
                        type_id = 5
                        model_id = notif.trip_id.id
                    elif notif.notif_type == "trip_pick_up_6":
                        type_id = 6
                        model_id = notif.trip_id.id
                    elif notif.notif_type == "worker_batch_assign_7":
                        type_id = 7
                        model_id = notif.batch_id.id
                    elif notif.notif_type == "warehouse_manager_validate_picking_8":
                        type_id = 8
                        model_id = notif.picking_id.id
                    elif notif.notif_type == "chat_9":
                        type_id = 9
                        partner_id = 0
                        partner_name = ""
                        partner_token = ""
                        if notif.chat_id.user_one.id == request.env.uid:
                            partner_id = notif.chat_id.user_two.id
                            partner_name = notif.chat_id.user_two.name
                            partner_token = notif.chat_id.user_two.user_token
                        if notif.chat_id.user_two.id == request.env.uid:
                            partner_id = notif.chat_id.user_one.id
                            partner_name = notif.chat_id.user_one.name
                            partner_token = notif.chat_id.user_one.user_token
                        model_id = str(notif.chat_id.id) + " , " + str(partner_id) + " , " + str(
                            partner_name) + " , " + str(partner_token)
                    elif notif.notif_type == "order_on_way_10":
                        type_id = 10
                        model_id = notif.order_id.id
                    elif notif.notif_type == "order_confirmed_11":
                        type_id = 11
                        model_id = notif.order_id.id
                    elif notif.notif_type == "order_ready_for_dispatch_12":
                        type_id = 12
                        model_id = notif.order_id.id
                    elif notif.notif_type == "order_out_for_delivery_13":
                        type_id = 13
                        model_id = notif.order_id.id
                    elif notif.notif_type == "trip_ready_to_send_14":
                        type_id = 14
                        model_id = notif.trip_id.id
                    user_notif.append({
                        "name": notif.name,
                        "description": notif.description,

                        "type_id": type_id,
                        "type_name": dict(notif._fields['notif_type'].selection).get(notif.notif_type),
                        "model_id": model_id

                        # "promotion_id": notif.promo_id.id,
                        # "trip_id": notif.trip_id.id,
                        # "picking_id": notif.picking_id.id,
                        # "order_id": notif.order_id.id,
                        # "batch_id": notif.batch_id.id

                    })
        if user_notif:
            Response.status = '200'
            response = {'status': 200, 'response': user_notif[::-1], 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'Error'}
        return response

    @http.route('/api/send-notifications', type='json', auth='user', methods=['POST'])
    def send_user_notification(self):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
        receiver = request.env['res.users'].sudo().search([('id', '=', req.get('receiver'))])
        chat_id = req.get('chat_id')
        message_name = "New Message!"
        message_description = "You have new message from" + user.name
        notif = self.send_notification(user, receiver, message_name, message_description)

        if notif:
            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'notification not sent'}
        return response

    def send_notification(user, receiver, message_name, message_description, notif_type_id=0, image_full_url=None,save_notif=True,notif_type='order',image=None,notifications_saved_id=None ):

        if save_notif :
            notifications_saved = request.env['sent.notification'].sudo().create({
                "name": message_name,
                "description": message_description,
                "users": [(4, receiver.id)],
                'image_full_url':image_full_url,
                'image':image,
                # "chat_id": 1,
                "notif_type": notif_type,
                'notif_type_id':notif_type_id
            })
            notifications_saved_id = notifications_saved.id
        details = ProductInfo()
        # server_Token = details.server_Token
        server_Token = details.fire_base
        device_Token = receiver.user_token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + server_Token,
        }

        body = {
            'notification': {'title': message_name,
                             'body': message_description,
                             'image': image_full_url
                             },
            'to':
                device_Token,
            'priority': 'high',
            "data": {
                # "sender_id": user.id,
                # "type_id": 9,
                # "chat_id": notifications_saved.chat_id.id,
                "notif_type": notif_type if notif_type else "",
                "notif_type_id": notif_type_id if notif_type_id else 0,
                'notification_id':notifications_saved_id
            },
        }


        notif = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        if notif:
            return True
        else:
            return False

    @http.route('/api/get-notifications', type='json', auth='public', methods=['POST'])
    def get_user_notification(self):
        req = json.loads(request.httprequest.data)
        notifications_list=[]
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        if user:
            notifications = request.env['sent.notification'].sudo().search([('users', 'in', [user.id])],order='id Desc',limit=20)


            for notification in notifications:
                value = {
                    "id":notification.id,
                    "name": notification.name,
                    "description": notification.description,
                    'image_full_url': notification.image_full_url if notification.image_full_url else "",
                    "notif_type": notification.notif_type if notification.notif_type else "",
                    'notif_type_id': notification.notif_type_id if notification.notif_type_id else 0
                }
                notifications_list.append(value)
            Response.status = '200'
            response = {'status': 200,'response':notifications_list, 'message': 'Success'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response