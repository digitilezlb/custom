# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def action_post(self):
    #     result = super(AccountMove, self).action_post()
    #     report = self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices", self.id)[0]
    #     filename = str(self.name) + '.pdf'
    #     pdf = self.env['ir.attachment'].sudo().create({
    #         'name': filename,
    #         'type': 'binary',
    #         'datas': base64.b64encode(report),
    #         'store_fname': filename,
    #         'res_model': 'account.move',
    #         'res_id': self.id,
    #         'mimetype': 'application/pdf',
    #         "public":True
    #     })
    #     self.attachment_id = [(4, pdf.id)]

    #     return result
