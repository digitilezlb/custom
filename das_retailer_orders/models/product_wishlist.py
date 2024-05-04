# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductWishlist(models.Model):
    _inherit = 'product.wishlist'

    product_template_id = fields.Many2one('product.template', string='Product Template')


class AccountMove(models.Model):
    _inherit = 'account.move'

    attachment_id = fields.Many2many('ir.attachment',
                                     string="attachment")
