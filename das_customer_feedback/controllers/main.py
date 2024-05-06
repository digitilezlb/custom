import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class CustomerFeedbackController(http.Controller):

    @http.route('/api/customer-feedback', type='json', auth='public', methods=['Post'], cors="*")
    def get_team(self):
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"

        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass

        if lang == "ar":
            if company_id:
                customer_feedbacks = request.env['customer.feedback'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)])
            else:
                customer_feedbacks = request.env['customer.feedback'].with_context(lang='ar_001').sudo().search([])
        else:

            if company_id:
                customer_feedbacks = request.env['customer.feedback'].sudo().search([('company_id', '=', company_id)])
            else:
                customer_feedbacks = request.env['customer.feedback'].sudo().search([])
        

        feedbacks = []
        if customer_feedbacks:
            for feedback in customer_feedbacks:

                values = {
                    "feedback_id": feedback.id,
                    "customer_name": feedback.name,
                    "customer_comment": feedback.customer_comment if feedback.customer_comment else "",
                    "customer_image": "/web/content/" + str(feedback.customer_image_attachment.id) if feedback.customer_image_attachment.id else "",

                    }
                feedbacks.append(values)
            Response.status = '200'
            response = {'status': 200, 'response': feedbacks, 'message': 'List Of Customers Feedback Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Customer Feedback Found!'}
        return response
