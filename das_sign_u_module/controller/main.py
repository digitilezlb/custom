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


class CustomResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code


class SignUp(http.Controller):
    version = ProductInfo.version
    def hash_number(self, number):
        number_str = str(number)
        sha256_hash = hashlib.sha256()
        sha256_hash.update(number_str.encode('utf-8'))
        hashed_number = sha256_hash.hexdigest()
        return hashed_number

    @http.route(version + 'login', type='json', auth="public", methods=['POST'], cors='*')
    def authenticate(self, db, login, password, base_location=None):
        # user = request.env['res.users'].sudo().search([('login', '=', login)])

        req = json.loads(request.httprequest.data)
        params = req.get("params")
        user = request.env['res.users'].sudo().search([('login', '=', login)])

        if user:
            if user.partner_id.is_client != True:
                company_id = params.get("company_id")

            password_valid = False
            # try:
            #     if user.partner_id.is_client != True:
            #         if user.is_log_in == True:
            #             Response.status = '403'
            #             response = {
            #                 'status': 403,
            #                 'message': 'User is logged in!'
            #             }
            #
            #             return response
            # except:
            #     pass
            if user:
                password_valid = user._check_credentials_api(password, {'interactive': True}, user.id)

                if user.partner_id.is_client != True:
                    if user.company_id.id != company_id:
                        Response.status = '406'

                        return {'status': 406, 'message': 'Different Company!'}

            if user and password_valid:
                if not http.db_filter([db]):
                    raise AccessError("Database not found.")
                pre_uid = request.session.authenticate(db, login, password)
                if pre_uid != request.session.uid:
                    return {'uid': None}
                request.session.db = db
                registry = odoo.modules.registry.Registry(db)
                with registry.cursor() as cr:
                    try:
                        if user.partner_id.is_client == True:
                            role = "Client"
                        elif user.partner_id.is_driver == True:
                            role = "Driver"
                        elif user.partner_id.is_chef == True:
                            role = "Chef"
                        elif user.partner_id.is_manager == True:
                            role = "Manager"
                        else:
                            role = "no role"
                    except:
                        role = "no role"
                    env = odoo.api.Environment(cr, request.session.uid, request.session.context)
                    if not request.db and not request.session.is_explicit:
                        http.root.session_store.rotate(request.session, env)
                        request.future_response.set_cookie(
                            'session_id', request.session.sid,
                            max_age=http.SESSION_LIFETIME, httponly=True
                        )
                    Response.status = '200'
                    info = env['ir.http'].session_info()
                    info["role"] = role
                    if user.partner_id.is_chef == True:
                        info["Kitchen_id"] = user.partner_id.kitchen_id.id if user.partner_id.kitchen_id else None
                    else:
                        info["Kitchen_id"] = None
                    user.write({
                        'is_log_in':True,
                        'log_time' : datetime.now()
                    })
                    return info
            else:
                Response.status = '401'
                response = {
                    'status': 401,
                    'message': 'Wrong Credential!'
                }
        else:
            Response.status = '404'
            response = {
                'status': 404,
                'message': 'User Not Found!'
            }
        return response

    @http.route(version + 'login-next', type='json', auth="public", methods=['POST'], cors='*')
    def authenticate_next(self, db, login, password, base_location=None):
        # user = request.env['res.users'].sudo().search([('login', '=', login)])

        req = json.loads(request.httprequest.data)
        params = req.get("params")
        user = request.env['res.users'].sudo().search([('login', '=', login)])

        if user:
            if user.partner_id.is_client != True:
                company_id = params.get("company_id")

            password_valid = False

            if user:
                password_valid = user._check_credentials_api(password, {'interactive': True}, user.id)

                if user.partner_id.is_client != True:
                    if user.company_id.id != company_id:
                        Response.status = '200'

                        return {'status': 200, 'message': 'Different Company!'}

            if user and password_valid:
                if not http.db_filter([db]):
                    raise AccessError("Database not found.")
                pre_uid = request.session.authenticate(db, login, password)
                if pre_uid != request.session.uid:
                    return {'uid': None}
                request.session.db = db
                registry = odoo.modules.registry.Registry(db)
                with registry.cursor() as cr:
                    try:
                        if user.partner_id.is_client == True:
                            role = "Client"
                        elif user.partner_id.is_driver == True:
                            role = "Driver"
                        elif user.partner_id.is_chef == True:
                            role = "Chef"
                        elif user.partner_id.is_manager == True:
                            role = "Manager"
                        else:
                            role = "no role"
                    except:
                        role = "no role"
                    env = odoo.api.Environment(cr, request.session.uid, request.session.context)
                    if not request.db and not request.session.is_explicit:
                        http.root.session_store.rotate(request.session, env)
                        request.future_response.set_cookie(
                            'session_id', request.session.sid,
                            max_age=http.SESSION_LIFETIME, httponly=True
                        )
                    Response.status = '200'
                    info = env['ir.http'].session_info()
                    info["role"] = role
                    if user.partner_id.is_chef == True:
                        info["Kitchen_id"] = user.partner_id.kitchen_id.id if user.partner_id.kitchen_id else None
                    else:
                        info["Kitchen_id"] = None
                    user.write({
                        'is_log_in': True,
                        'log_time': datetime.now()
                    })
                    return info
            else:
                Response.status = '200'
                response = {
                    'status': 200,
                    'message': 'Wrong Credential!'
                }
        else:
            Response.status = '200'
            response = {
                'status': 200,
                'message': 'User Not Found!'
            }
        return response
    @http.route(version + 'session', type='json', auth="public", cors='*', methods=['POST'])
    def get_session_id(self):
        return {"session_id": request.session.sid}

    @http.route(version + 'registration', type='json', auth='public', methods=['Post'], cors="*")
    def create_user_registration(self):
        req = json.loads(request.httprequest.data)
        _login = req.get("login")
        _name = req.get("name")
        _password = req.get("password")

        if not _name:
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter name'}
            return response
        elif _name.strip() == '':
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter name'}
            return response

        if not _password:
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter password'}
            return response
        elif _password.strip() == '':
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter password'}
            return response

        if not _login:
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter login'}
            return response
        elif _login.strip() == '':
            Response.status = '401'
            response = {'status': 401, 'message': 'You must enter login'}
            return response

        if _login:
            user_found = request.env['res.users'].sudo().search([('login', '=', _login)])

            if user_found:
                Response.status = '401'
                response = {'status': 401, 'message': 'Duplicated login'}
                return response
        ## if _name:
        ##     user_found = request.env['res.users'].sudo().search([('name', '=', _name)])
        ##
        ##     if user_found:
        ##         Response.status = '401'
        ##         response = {'status': 401, 'message': 'Duplicated name'}
        ##         return response

        vals = {
            'name': _name,
            'login': _login,
            'password': _password,
            'tz': ProductInfo.asia_beirut,
            'groups_id': [(4, request.env.ref('base.group_portal').id)],
        }
        user = request.env['res.users'].sudo().create(vals)
        if user:
            Response.status = '200'
            response = {'status': 200, 'response': {"created_id": user.id}, 'message': 'User Created'}
            # try:

            partner = user.partner_id
            if "@" in _login:
                vals = {
                    "email": _login,
                    "city": req.get("city") if req.get("city") else "",
                    "mobile": req.get("mobile") if req.get("mobile") else "",
                    "street": req.get("street") if req.get("street") else "",
                    "partner_latitude": req.get("latitude") if req.get("latitude") else 0,
                    "partner_longitude": req.get("longitude") if req.get("longitude") else 0,
                    "is_client": True
                }
            else:
                vals = {
                    "mobile": _login,
                    "city": req.get("city") if req.get("city") else "",
                    "email": req.get("email") if req.get("email") else "",
                    "street": req.get("street") if req.get("street") else "",
                    "partner_latitude": req.get("latitude") if req.get("latitude") else 0,
                    "partner_longitude": req.get("longitude") if req.get("longitude") else 0,
                    "is_client": True
                }
            partner.sudo().write(vals)

            if req.get("latitude"):
                lat = req.get("latitude")
            else:
                lat = 0.0
            if req.get("longitude"):
                lng = req.get("longitude")
            else:
                lng = 0.0


            try:
                detail = ProductInfo()
                vals = detail.calcul_for_address(lat, lng)

                if vals:
                    retailer_user = request.env['res.users'].sudo().search([('id', '=', user.id)])


                    values = {
                        "name": retailer_user.partner_id.name,
                        "mobile": retailer_user.partner_id.mobile if retailer_user.partner_id.mobile else "",
                        "phone": retailer_user.partner_id.phone if retailer_user.partner_id.phone else "",

                        "city": retailer_user.partner_id.city if retailer_user.partner_id.city else "",
                        "street": retailer_user.partner_id.street if retailer_user.partner_id.street else "",
                        "street2": retailer_user.partner_id.street2 if retailer_user.partner_id.street2 else "",
                        "partner_latitude": lat,
                        "partner_longitude": lng,
                        "parent_id": retailer_user.partner_id.id,
                        "is_client": True,
                        # "is_member": False,
                        "is_driver": False,
                        "is_manager": False,
                        "type": 'delivery',
                        "zone_id": vals['zone_id'],
                        "is_default_address": True
                    }

                    new_address = request.env['res.partner'].sudo().create(values)
                    
            except:
                pass

            # except:
            #     pass
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Added!'}
        return response

    @http.route(version + 'registration-next', type='json', auth='public', methods=['Post'], cors="*")
    def create_user_registration_next(self):
        req = json.loads(request.httprequest.data)
        _login = req.get("login")
        _name = req.get("name")
        _password = req.get("password")

        if not _name:
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter name'}
            return response
        elif _name.strip() == '':
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter name'}
            return response

        if not _password:
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter password'}
            return response
        elif _password.strip() == '':
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter password'}
            return response

        if not _login:
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter login'}
            return response
        elif _login.strip() == '':
            Response.status = '200'
            response = {'status': 200, 'message': 'You must enter login'}
            return response

        if _login:
            user_found = request.env['res.users'].sudo().search([('login', '=', _login)])

            if user_found:
                Response.status = '200'
                response = {'status': 200, 'message': 'Duplicated login'}
                return response
        ## if _name:
        ##     user_found = request.env['res.users'].sudo().search([('name', '=', _name)])
        ##
        ##     if user_found:
        ##         Response.status = '401'
        ##         response = {'status': 401, 'message': 'Duplicated name'}
        ##         return response

        vals = {
            'name': _name,
            'login': _login,
            'password': _password,
            'tz': ProductInfo.asia_beirut,
            'groups_id': [(4, request.env.ref('base.group_portal').id)],
        }
        user = request.env['res.users'].sudo().create(vals)
        if user:
            Response.status = '200'
            response = {'status': 200, 'response': {"created_id": user.id}, 'message': 'User Created'}
            # try:

            partner = user.partner_id
            if "@" in _login:
                vals = {
                    "email": _login,
                    "city": req.get("city") if req.get("city") else "",
                    "mobile": req.get("mobile") if req.get("mobile") else "",
                    "street": req.get("street") if req.get("street") else "",
                    "partner_latitude": req.get("latitude") if req.get("latitude") else 0,
                    "partner_longitude": req.get("longitude") if req.get("longitude") else 0,
                    "is_client": True
                }
            else:
                vals = {
                    "mobile": _login,
                    "city": req.get("city") if req.get("city") else "",
                    "email": req.get("email") if req.get("email") else "",
                    "street": req.get("street") if req.get("street") else "",
                    "partner_latitude": req.get("latitude") if req.get("latitude") else 0,
                    "partner_longitude": req.get("longitude") if req.get("longitude") else 0,
                    "is_client": True
                }
            partner.sudo().write(vals)

            if req.get("latitude"):
                lat = req.get("latitude")
            else:
                lat = 0.0
            if req.get("longitude"):
                lng = req.get("longitude")
            else:
                lng = 0.0

            try:
                detail = ProductInfo()
                vals = detail.calcul_for_address(lat, lng)

                if vals:
                    retailer_user = request.env['res.users'].sudo().search([('id', '=', user.id)])

                    values = {
                        "name": retailer_user.partner_id.name,
                        "mobile": retailer_user.partner_id.mobile if retailer_user.partner_id.mobile else "",
                        "phone": retailer_user.partner_id.phone if retailer_user.partner_id.phone else "",

                        "city": retailer_user.partner_id.city if retailer_user.partner_id.city else "",
                        "street": retailer_user.partner_id.street if retailer_user.partner_id.street else "",
                        "street2": retailer_user.partner_id.street2 if retailer_user.partner_id.street2 else "",
                        "partner_latitude": lat,
                        "partner_longitude": lng,
                        "parent_id": retailer_user.partner_id.id,
                        "is_client": True,
                        # "is_member": False,
                        "is_driver": False,
                        "is_manager": False,
                        "type": 'delivery',
                        "zone_id": vals['zone_id'],
                        "is_default_address": True
                    }

                    new_address = request.env['res.partner'].sudo().create(values)

            except:
                pass

            # except:
            #     pass
        else:
            Response.status = '200'
            response = {'status': 200, 'message': 'User Not Added!'}
        return response

    # @http.route(version + 'change-password-new', type='json', auth='user', methods=['Post'], cors="*")
    # def change_password_new(self):
    #     # 204
    #     req = json.loads(request.httprequest.data)
    #
    #     old_password = str(req.get('old_password'))
    #
    #     password_valid = False
    #     user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])
    #     if user:
    #         password_valid = user._check_credentials_api(old_password, {'interactive': True}, user.id)
    #         if password_valid:
    #             user.sudo().write({'password': req.get('password')})
    #             # request.session.logout(keep_db=True)
    #             Response.status = '200'
    #             response = {'status': 200, 'message': 'Success'}
    #         else:
    #             Response.status = '401'
    #             response = {'status': 401, 'message': 'Wrong Old Password'}
    #     else:
    #         Response.status = '404'
    #         response = {'status': 404, 'message': 'User Not Found'}
    #     return response



    @http.route(version + 'change-password-new', type='json', auth="user", methods=['POST'], cors='*')
    def change_password_new(self):
        # user = request.env['res.users'].sudo().search([('login', '=', login)])

        req = json.loads(request.httprequest.data)

        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        if user:

            password_valid = False
            oldpassword = req.get('oldpassword')
            password_valid = user._check_credentials_api(oldpassword, {'interactive': True}, user.id)

            if user and password_valid:
                user.sudo().write({'password': str(req.get('password'))})

                Response.status = '200'
                response = {'status': 200, 'message': 'Success'}
            else:

                Response.status = '401'
                response = {'status': 401, 'message': 'Wrong Old Password'}
        else:
            Response.status = '404'
            response = {
                'status': 404,
                'message': 'User Not Found!'
            }
        return response

    @http.route(version + 'change-password', type='json', auth="public", methods=['POST'], cors='*')
    def change_password(self):
        # user = request.env['res.users'].sudo().search([('login', '=', login)])

        req = json.loads(request.httprequest.data)

        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])

        if user:

            password_valid = False
            oldpassword = req.get('oldpassword')
            password_valid = user._check_credentials_api(oldpassword, {'interactive': True}, user.id)



            if user and password_valid:
                user.sudo().write({'password': str(req.get('password'))})

                Response.status = '200'
                response = {'status': 200, 'message': 'Success'}
            else:

                Response.status = '401'
                response = {'status': 401, 'message': 'Wrong Old Password'}
        else:
            Response.status = '404'
            response = {
                'status': 404,
                'message': 'User Not Found!'
            }
        return response

    @http.route(version + 'delete-account', type='json', auth='user', methods=['Post'], cors="*")
    def delete_account(self):
        # 204
        req = json.loads(request.httprequest.data)

        user = request.env["res.users"].sudo().search([("id", "=", req.get('user_id'))])
        if user:
            user.sudo().write({'password': "@@@@123@@@"})
            try:
                request.session.logout(keep_db=True)
            except:
                pass
            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
        return response

    @http.route(version + 'delete-account-user', type='json', auth='public', methods=['Post'], cors="*")
    def delete_account_user(self):
        # 204
        req = json.loads(request.httprequest.data)

        user = request.env["res.users"].sudo().search([("id", "=", req.get('user_id'))])
        if user:
            user.sudo().write({'password': "@@@@123@@@"})
            # try:
            #     request.session.logout(keep_db=True)
            # except:
            #     pass
            Response.status = '200'
            response = {'status': 200, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}
        return response

    @http.route(version + 'wassim-akel-assad', type='json', auth='public', methods=['Post'], cors="*")
    def wassim_akel(self):
        # 204

        users = request.env["res.users"].sudo().search([])

        if users:
            user_list = []
            for user in users:
                values = {
                    "user_id": user.id,
                    "login": user.login,
                    "user_token": user.user_token,
                    "is_log_in":user.is_log_in,
                    "user_owner":user.user_owner,
                    "user_admin":user.user_admin,

                }
                user_list.append(values)
            Response.status = '200'
            response = {'status': 200, 'users': user_list, 'message': 'Success'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User Not Found'}

        return response

    @http.route(version + 'logout', type='json', auth="none", cors='*')
    def logout_appi(self, redirect='/web'):


        request.session.logout(keep_db=True)
        Response.status = '200'
        response = {'status': 200, 'message': 'succ'}

        return response

    @http.route(version + 'logout-user', type='json', auth="user",methods=['Post'], cors='*')
    def logout_user(self, redirect='/web'):
        user = request.env['res.users'].sudo().search([('id', '=', request.env.uid)])

        user.write({
            'is_log_in': False,
            'log_time': datetime.now()
        })

        request.session.logout(keep_db=True)
        Response.status = '200'
        response = {'status': 200, 'message': 'succ'}

        return response

    @http.route(version + 'logout-public', type='json', auth="public", methods=['Post'], cors='*')
    def logout_public(self, redirect='/web'):
        req = json.loads(request.httprequest.data)
        user = request.env["res.users"].sudo().search([("id", "=", req.get('user_id'))])
        if user:
            user.write({
                'is_log_in': False,
                'log_time': datetime.now()
            })

            request.session.logout(keep_db=True)
            Response.status = '200'
            response = {'status': 200, 'message': 'succ'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'User not found!'}
        return response


    @http.route(version + 'user-profile', type='json', auth='public', methods=['Post'], cors="*")
    def get_user_profile(self, **res):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if ('https' in base_url) == False:
            base_url = base_url.replace('http', 'https')
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        if user.partner_id:
            if user.partner_id.is_client == True:
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
                "user_mobile": user.partner_id.mobile if user.partner_id.mobile else "",
                "user_role": role,
                "company_id": user.company_id.id,
                # "user_city_id": user.partner_id.city if user.partner_id.city  else "",
                "user_city_name": user.partner_id.city if user.partner_id.city else "",
                # "user_street_id": user.partner_id.street_id.id,
                "user_street_name": user.partner_id.street if user.partner_id.street else "",
                "user_address_details": user.partner_id.street2 if user.partner_id.street2 else "",
                "user_email": user.partner_id.email if user.partner_id.email else "",
                "role":role,
                "user_image": "/web/content/" + str(
                    user.partner_id.team_member_image_attachment.id) if user.partner_id.team_member_image_attachment.id else "",
                "user_image_full_path": base_url + "/web/content/" + str(user.partner_id.team_member_image_attachment.id) if user.partner_id.team_member_image_attachment.id else "",

            }
            Response.status = '200'
            response = {'status': 200, 'response': vals, 'message': 'profile Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No profile Found!'}
        return response

    def is_internal_user(self, user):
        # Check if the user belongs to the 'base.group_user' group
        return user.has_group('base.group_user')

    def is_portal_user(self, user):
        # Check if the user belongs to the 'base.group_portal' group
        return user.has_group('base.group_portal')

    @http.route(version + 'update-profile', type='json', auth='public', methods=['Post'], cors="*")
    def update_user_profile(self, **res):
        req = json.loads(request.httprequest.data)
        user = request.env['res.users'].sudo().search([('id', '=', req.get('user_id'))])
        detail = ProductInfo()
        if user.partner_id:
            # partner = request.env['res.partner'].sudo().search([('id', '=', user.partner_id.id)])
            req = json.loads(request.httprequest.data)
            # order_id = req.get('f_name')

            if req.get('email'):
                _email = req.get('email')
                if _email.strip() != '':
                    if detail.is_valid_email(_email.strip()) == False:
                        Response.status = 401
                        response = {'status': 401, 'message': 'email not valid!!'}
                        return response

                    partner = user.partner_id
                    partner_found = request.env['res.partner'].sudo().search(
                        [('email', '=', _email.strip()), ('id', '!=', partner.id)])
                    if partner_found:
                        Response.status = '401'
                        response = {'status': 401, 'message': 'Duplicated email'}
                        return response

            if req.get('name'):
                _name = req.get('name')
                if _name.strip() != '':
                    user_found = request.env['res.users'].sudo().search(
                        [('name', '=', _name.strip()), ('id', '!=', user.id)])
                    if user_found:
                        Response.status = '401'
                        response = {'status': 401, 'message': 'Duplicated name'}
                        return response

                    user.partner_id.write({
                        "name": _name.strip()
                    })

            if req.get('email'):
                _email = req.get('email')
                if detail.is_valid_email(_email.strip()):
                    user.partner_id.write({
                        "email": _email.strip()
                    })
                else:
                    user.partner_id.write({
                        "email": False
                    })
            else:
                user.partner_id.write({
                    "email": False
                })

            if req.get('city'):
                _city = req.get('city')
                if _city.strip() != '':
                    user.partner_id.write({
                        "city": _city.strip()
                    })

            if req.get('street'):
                _street = req.get('street')
                if _street.strip() != '':
                    user.partner_id.write({
                        "street": _street.strip()
                    })

            if req.get('near'):
                _near = req.get('near')
                if _near.strip() != '':
                    user.partner_id.write({
                        "street2": _near.strip()
                    })
                else:
                    user.partner_id.write({
                        "street2": False
                    })
            else:
                user.partner_id.write({
                    "street2": False
                })

            if req.get('image'):
                if req.get('image') != '-1':
                    user.partner_id.write({
                        "image_1920": req.get('image')
                    })


                else:
                    user.partner_id.write({
                        "image_1920": False,
                        "team_member_image_attachment": False
                    })

            Response.status = '200'
            response = {'status': 200, 'message': 'profile Updated'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No profile Found!'}
        return response
