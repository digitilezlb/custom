from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    default = fields.Boolean(string="Default", default=False, readonly=False, store=True)
    def set_as_default(self):
        for rec in self:
            all_ads = rec.env['product.product'].sudo().search([('product_tmpl_id','=',self.product_tmpl_id.id)])
            for ad in all_ads:
                ad.default = False
            rec.default = True