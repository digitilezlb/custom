# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    is_working_day = fields.Boolean()
    # is_working_day_1 = fields.Boolean()
    _sql_constraints = [
        ('unique_company_calendar', 'unique(company_id)', 'Company must be unique.'),
    ]

    def set_as_working_hours(self):
        for rec in self:
            all = rec.env['resource.calendar'].sudo().search([('company_id', '=', self.env.company.id)])
            for w in all:
                w.is_working_day = False
            rec.is_working_day = True

