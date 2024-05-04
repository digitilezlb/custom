from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response
import base64
import json
import logging
from datetime import date, datetime
import requests

from datetime import datetime, timedelta
import pytz
# from odoo.addons.smile_log.tools import SmileDBLogger
from odoo.addons.das_publicfunction.controller.main import ProductInfo

from odoo.addons.das_first_order.controller.main import FirstOrderDiscount

from odoo.addons.web.models.ir_http import Http
from odoo.addons.das_user_notification.controller.main import Notification


class AddToCardControllerHttp(http.Controller):

    @http.route(ProductInfo.version + 'cart-items-count-http', type='http', auth='public', methods=['Get'], cors="*")
    def cart_items_count(self):
        Product_Info = ProductInfo()
        order_line_list = []

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'draft')])

        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'user does not have cart'}
            return Response(json.dumps(response), content_type='application/json;charset=utf-8',
                            status=response['status'])



        order_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation.id)])
        if order_lines:
            order_lines_count = len(order_lines)
        else:
            order_lines_count = 0
        Response.status = '200'
        response = {'status': 200, 'order_lines_count': order_lines_count, 'message': 'order line count'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])


    @http.route(ProductInfo.version + 'cart-items-http', type='http', auth='public', methods=['Get'], cors="*")
    def cart_items(self):
        Product_Info = ProductInfo()
        order_line_list = []

        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        retailer_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        quotation = request.env['sale.order'].sudo().search(
            [('partner_id', '=', retailer_user.partner_id.id), ('state', '=', 'draft')])

        if not quotation:
            Response.status = '404'
            response = {'status': 404, 'message': 'user does not have cart'}
            return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')

        quotation_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', quotation.id)])
        for quotation_line in quotation_lines:
            order_line_value = {
                'order_line_id': quotation_line.id,
                'product_id': quotation_line.product_id.id,
                'product_tmpl_id': quotation_line.product_id.product_tmpl_id.id,
                'quantity': quotation_line.product_uom_qty,
                'price_unit': quotation_line.price_unit,
                'notes': quotation_line.notes,
                'addons_note': quotation_line.addons_note,
                'removable_ingredients_note': quotation_line.removable_ingredients_note,
                'combo_content': quotation_line.combo_content,
                "product_main_image": "/web/content/" + str(
                    quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",
                "product_main_image_path": base_url + "/web/content/" + str(
                    quotation_line.product_id.image_attachment.id) if quotation_line.product_id.image_attachment.id else "",

            }
            order_line_list.append(order_line_value)


        Response.status = '200'
        response = {'status': 200, 'order_lines': order_line_list, 'message': 'order line list'}
        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])
