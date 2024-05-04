from odoo import api, fields, models


class ProductSaved(models.Model):
    _name = "product.saved"
    _description = "Product saved for later"

    product_id = fields.Many2one('product.product', string='Product')
    partner_id = fields.Many2one('res.partner', string="Retailer")
