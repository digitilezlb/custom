
import json
from odoo.http import Response
from odoo import http,exceptions
from odoo.http import request
from werkzeug.wrappers import Response as REEEsp
import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
import hashlib
from odoo.addons.das_publicfunction.controller.main import ProductInfo



class SignUpHttp(http.Controller):
    @http.route('/api/user-profile-http', type='http', auth='public', methods=['Get'],cors="*")
    def get_user_profile(self, **res):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if  ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        try:
            user_id = int(request.params.get('user_id'))
        except:
            user_id = -1

        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        
        if user.partner_id:
            if  user.partner_id.is_client == True:
                role = "Client"
            elif user.partner_id.is_driver == True:
                role = "Driver"
            elif user.partner_id.is_chef == True:
                role = "Chef"
            elif user.partner_id.is_manager == True:
                role = "Manager"
            else:
                role = "no role"
            vals = {
                "user_name": user.name,
                "user_login": user.login,
                "user_mobile": user.partner_id.mobile if user.partner_id.mobile  else "",
                "user_role": role,
                "company_id": user.company_id.id,
                # "user_city_id": user.partner_id.city if user.partner_id.city  else "",
                "user_city_name": user.partner_id.city if user.partner_id.city  else "",
                # "user_street_id": user.partner_id.street_id.id,
                "user_street_name": user.partner_id.street if user.partner_id.street  else "",
                "user_address_details": user.partner_id.street2 if user.partner_id.street2  else "",
                "user_email": user.partner_id.email if user.partner_id.email  else "",
                "user_image": base_url + "/web/content/" + str(user.partner_id.team_member_image_attachment.id) if user.partner_id.team_member_image_attachment.id else "",


            }
            Response.status = '200'
            response = {'status':200, 'response': vals, 'message': 'profile Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No profile Found!'}

        return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    def is_internal_user(self, user):
        # Check if the user belongs to the 'base.group_user' group
        return user.has_group('base.group_user')

    def is_portal_user(self, user):
        # Check if the user belongs to the 'base.group_portal' group
        return user.has_group('base.group_portal')