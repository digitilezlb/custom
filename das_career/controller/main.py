from odoo.http import request
from odoo.http import Response
import json
from odoo import http
import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
import hashlib
from algoliasearch.recommend_client import RecommendClient
from algoliasearch.search_client import SearchClient
import os
from odoo.addons.das_publicfunction.controller.main import ProductInfo


class CareerInformation(http.Controller):

    @http.route('/api/career-information-http', type='json', auth="public", cors='*', methods=['POST'])
    def get_career_information(self):
        # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        if req.get('company_id'):
            career_id = request.env['career.information'].sudo().search(
                [('company_id', '=', req.get('company_id'))])
        else:
            career_id = request.env['career.information'].sudo().search(
                [],limit=1)
        if career_id:
            vals = {
                "title": career_id.title if career_id.title else "",
                "description": Product_Info.change_parag_to_line(career_id.description) if career_id.description else "",
                "title1": career_id.title1 if  career_id.title1 else "",
                "icon1":   "/web/content/" + str(
                    career_id.icon1_attachment.id) if career_id.icon1_attachment.id else "",
                "description1": Product_Info.change_parag_to_line(career_id.description1) if career_id.description1 else "",
                "title2": career_id.title2 if  career_id.title2 else "",
                "icon2":  "/web/content/" + str(
                    career_id.icon2_attachment.id) if  career_id.icon2_attachment.id else "",
                "description2": Product_Info.change_parag_to_line(career_id.description2) if career_id.description2 else "",
                "title3": career_id.title3 if career_id.title3 else "",
                "icon3":  "/web/content/" + str(
                    career_id.icon3_attachment.id) if career_id.icon3_attachment.id else "",
                "description3": Product_Info.change_parag_to_line(career_id.description3) if career_id.description3 else "",
                "vacancies_title": career_id.vacancies_title  if career_id.vacancies_title else "",
                "vacancies_description": Product_Info.change_parag_to_line(career_id.vacancies_description) if career_id.vacancies_description else ""
            }
            Response.status = '200'
            response = {'status': 200, 'response': vals,
                        'message': 'career information Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found'}
        
        return response
        # return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route('/api/job-positions-http', type='json', auth="public", cors='*', methods=['POST'])
    def get_job_positions(self):
        Product_Info = ProductInfo()
        req = json.loads(request.httprequest.data)
        if  req.get('company_id'):
            jobs = request.env['hr.job'].sudo().search(
                [('is_published', '=', True), ('is_cv', '=', False),('company_id','=', req.get('company_id'))])
        else:
            jobs = request.env['hr.job'].sudo().search(
                [('is_published', '=', True), ('is_cv', '=', False)])
        job_list = []
        if jobs:
            for job in jobs:
                if job.address_id.state_id.name:
                    state_name = str(job.address_id.state_id.name)
                else :
                    state_name = ""

                if job.address_id.city_id.name:
                    city_name = str(job.address_id.city_id.name)
                else:
                    city_name = ""

                if job.address_id.street:
                    street_name = str(job.address_id.street)
                else:
                    street_name = ""

                job_list.append({
                    "job_id": job.id,
                    "job_name": job.name if job.name else "",
                    "job_description": Product_Info.change_parag_to_line(job.description) if job.description else "",
                    "address": state_name + " " + city_name  + " " + street_name ,
                    "image":"/web/content/" + str(job.image_attachment.id) if job.image_attachment.id else "",
                    "created_at": job.create_date
                })
            Response.status = '200'
            response = {'status': 200, 'response': job_list,
                        'message': 'job positions Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found'}
        return response
        # return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

    @http.route('/api/job-apply-form-http', type='json', auth="public", cors='*', methods=['POST'])
    def job_apply_form(self):
        req = json.loads(request.httprequest.data)
        detail = ProductInfo()
        job = request.env['hr.job'].sudo().search(
            [('id', '=', req.get('job_id'))])
        if job:
            if detail.is_valid_email(req.get('email'))==False:
                Response.status = '200'
                response = {'status': 200, 'message': 'email not valid!!'}
                return response
            vals = {
                "job_id": job.id,
                "partner_name": req.get('full_name'),
                "name": req.get('full_name'),
                "email_from": req.get('email'),
                "description": req.get('message'),
                "partner_mobile": req.get('mobile'),
            }
            hr_applicant = request.env['hr.applicant'].sudo().create(vals)
            image_att = request.env['ir.attachment'].sudo().create({
                "name": "CV",
                'type': 'binary',
                'datas': req.get('file'),
                'res_model': 'hr.applicant',
                'res_id': hr_applicant.id,
            })
            if hr_applicant:
                Response.status = '200'
                response = {'status': 200, 'message': 'form created successfully'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'form not created'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found'}
        return response

    @http.route('/api/cv-apply-form-http', type='json', auth="public", cors='*', methods=['POST'])
    def cv_apply_form(self):
        req = json.loads(request.httprequest.data)
        job = request.env['hr.job'].sudo().search(
            [('id', '=', request.env.ref('das_career.general_job').id)])
        if job:
            vals = {
                "job_id": job.id,
                "partner_name": req.get('full_name'),
                "name": req.get('full_name'),
                "email_from": req.get('email'),
                "description": req.get('message'),
                "partner_mobile": req.get('mobile'),
            }
            hr_applicant = request.env['hr.applicant'].sudo().create(vals)
            image_att = request.env['ir.attachment'].sudo().create({
                "name": "CV",
                'type': 'binary',
                'datas': req.get('file'),
                'res_model': 'hr.applicant',
                'res_id': hr_applicant.id,
            })
            if hr_applicant:
                Response.status = '200'
                response = {'status': 200, 'message': 'form created successfully'}
            else:
                Response.status = '404'
                response = {'status': 404, 'message': 'form not created'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No data Found'}
        return response
