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


class DasUserSecure(http.Controller):
    version = ProductInfo.version

    @http.route(version + 'enable-maintenance-mode', type='json', auth='public', methods=['Post'], cors="*")
    def enable_maintenance_mode(self):
        # 204
        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])
        if user:
            company_id = req.get('company_id')
            if user[0].user_admin:
                if company_id :
                    companies = request.env['res.company'].sudo().search([('id','=',company_id)])
                else:
                    companies = request.env['res.company'].sudo().search([])

                for company in companies:
                    company.sudo().write({'maintenance_mode': True})

                Response.status = '200'
                response = {'status': 200, 'message': 'Done!'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Allowed To Do This Action!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response

    @http.route(version + 'disable-maintenance-mode', type='json', auth='public', methods=['Post'], cors="*")
    def disable_maintenance_mode(self):

        req = json.loads(request.httprequest.data)
        user_id = req.get('user_id')
        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])
        if user:
            company_id = req.get('company_id')
            if user[0].user_admin:
                if company_id:
                    companies = request.env['res.company'].sudo().search([('id', '=', company_id)])
                else:
                    companies = request.env['res.company'].sudo().search([])

                for company in companies:
                    company.sudo().write({'maintenance_mode': False})

                Response.status = '200'
                response = {'status': 200, 'message': 'Done!'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Allowed To Do This Action!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response

    @http.route(version + 'make-user-admin', type='json', auth='public', methods=['Post'], cors="*")
    def make_user_admin(self):
        # 204
        req = json.loads(request.httprequest.data)

        user_id = req.get('user_id')


        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if user:

            user.sudo().write({'user_admin': True})

            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
        return response

    @http.route(version + 'disable-all-users', type='json', auth='public', methods=['Post'], cors="*")
    def disable_all_users(self):

        req = json.loads(request.httprequest.data)

        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])


        if user:
            if user[0].user_admin:
                company_id = req.get('company_id')
                if company_id :
                    users = request.env['res.users'].sudo().search([('user_admin', '!=', True),('company_id','=',company_id)])
                    companies = request.env['res.company'].sudo().search([('id','=',company_id)])
                else:
                    users = request.env['res.users'].sudo().search([('user_admin', '!=', True)])
                    companies = request.env['res.company'].sudo().search([])


                for user in users:
                    user.sudo().write({'active': False})

                for company in companies:
                    company.sudo().write({'disable_users': True})

                Response.status = '200'
                response = {'status': 200, 'message': 'Done!'}
                
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Allowed To Do This Action!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response

    @http.route(version + 'enable-all-users', type='json', auth='public', methods=['Post'], cors="*")
    def enable_all_users(self):

        req = json.loads(request.httprequest.data)

        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])

        if user:
            if user[0].user_admin:
                company_id = req.get('company_id')
                if company_id :
                    users = request.env['res.users'].sudo().search([('active', '=', False),('user_admin', '!=', True),('company_id','=',company_id)])
                    companies = request.env['res.company'].sudo().search([('id', '=', company_id)])
                else:
                    users = request.env['res.users'].sudo().search([('active', '=', False),('user_admin', '!=', True)])
                    companies = request.env['res.company'].sudo().search([])
                # users = request.env['res.users'].sudo().search([('active', '=', False),('user_admin', '!=', True)])
                for user in users:
                    if user.login !='__system__' and user.login !='default' and user.login !='public'  and user.login !='portaltemplate' :
                        user.sudo().write({'active': True})

                for company in companies:
                    company.sudo().write({'disable_users': False})

                Response.status = '200'
                response = {'status': 200, 'message': 'Done!'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Allowed To Do This Action!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response

    @http.route(version + 'create-new-company', type='json', auth='public', methods=['Post'], cors="*")
    def create_new_company(self):

        req = json.loads(request.httprequest.data)

        user = request.env['res.users'].sudo().search([('id', '=', req.get("user_id"))])

        if user:
            if user[0].user_admin:
                parent_id = req.get('parent_id')

                company_name = req.get('name')

                company = request.env['res.company'].sudo().create(
                    {
                        "name": company_name,
                        "parent_id": parent_id if parent_id else False
                    }
                )


                Response.status = '200'
                response = {'status': 200, 'company_id': company.id,'message': 'Done!'}

            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'User Not Allowed To Do This Action!'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response