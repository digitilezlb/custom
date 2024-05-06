import json
from odoo.http import Response
from odoo import http
from odoo.http import request
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import re
import requests

from datetime import datetime
from odoo.addons.das_user_notification.controller.main import Notification


class ExternalAPI(http.Controller):
    version = ProductInfo.version
    @http.route(version + 'test-extrnal-api', type='json', auth='public', methods=['Post'], cors="*")
    def read_api(self):
        baseurl = "https://cms.fayssalbaccar.com/api/login"
        # login = baseurl + "auth/login"
        payload = {
                    "params": {
                                "db": "alfayssal",
                                     "login": "123456",
                                  "password": "password1",
                                  "company_id":1
                              }
                   }
        headers = {}

        response = requests.post(baseurl, json=payload,headers=headers)
        # print('---status_code-----------status_code-------status_code-------',# Response.status_code)

        # response.raise_for_status()

        r = response.json()
        # status_code =   # Response.status_code
        # if status_code == 200:
        #     # Response.status = '200'
        #     response = {'status': 200, 'message': 'OK!'}
        # else:
        #     # Response.status = status_code
        #     response = {'status': status_code, 'message': 'ERROR!'}
        ## if isinstance(response.json(), dict):
        ##     # If the response is a dictionary, it may contain an error message
        ##     print("Error:", response.json())
        ## else:
        ##     # Otherwise, assume it's a successful response
        ##     print(# Response.status_code)
        ##     print(response.json())

        # Response.status = '404'


        return response

    @http.route(version + 'client-login', type='json', auth='public', methods=['Post'], cors="*")
    def client_login_api(self):

        req = json.loads(request.httprequest.data)
        params = req.get("params")

        baseurl = req.get("baseurl") # "https://cms.fayssalbaccar.com"
        baseurl = baseurl + "/api/login"
        # payload = {
        #     "params": {
        #         "db": "alfayssal",
        #         "login": "123456",
        #         "password": "password1",
        #         "company_id": 1
        #     }
        # }
        payload = {"params":params}

        headers = {}

        response = requests.post(baseurl, json=payload, headers=headers)

        r = response.json()

        # status_code =    # Response.status_code
        # if status_code == 200:
        #     # Response.status = '200'
        #     response = {'status': 200,'result':r, 'message': 'OK!'}
        # else:
        #     # Response.status = status_code
        #     response = {'status': status_code, 'message': 'ERROR!'}
        #
        #
        # return response