from odoo import http
from odoo.http import request


class CustomWebPageController(http.Controller):

    @http.route('/terms-and-conditions', auth='public', website=True)
    def terms_and_conditions_page(self, **kwargs):
        # Fetch data if needed
        # data = request.env['your.model'].search([])

        # Render the view
        return http.request.render('das_terms_and_conditions_web_page.terms_and_conditions', {})

    @http.route('/privacy-policy', auth='public', website=True)
    def privacy_policy_page(self, **kwargs):
        # Fetch data if needed
        # data = request.env['your.model'].search([])

        # Render the view
        return http.request.render('das_terms_and_conditions_web_page.privacy_policy', {})

    @http.route('/support', auth='public', website=True)
    def support_page(self, **kwargs):
        # Fetch data if needed
        # data = request.env['your.model'].search([])

        # Render the view
        return http.request.render('das_terms_and_conditions_web_page.support', {})