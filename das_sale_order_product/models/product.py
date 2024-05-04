from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = "product.template"

    # location_shelf = fields.Many2one('stock.location', string="Location")
    discount = fields.Float(string="Discount %", required=True, default="0")
    # unit_code = fields.Many2one('unit.code', string="Unit Code")
    # pack_of = fields.Char(string="Pack")
    # pack_of_id = fields.Many2one('pack.of', string="Pack")
    new_bool = fields.Boolean()
    app_publish = fields.Boolean(default=False, string="Publish on App")
    # is_popular = fields.Boolean(string="Popular", default=False, readonly=False, store=True)
    
    def mark_as_new(self):
        self.new_bool = True
        self.website_ribbon_id = self.env.ref('website_sale.new_ribbon').id
    
    def remove_new(self):
        self.new_bool = False
        self.website_ribbon_id = False


# class UniteCode(models.Model):
#     _name = "unit.code"
#
#     name = fields.Char(string="Name", required=True)
    
# class PackOf(models.Model):
#     _name = "pack.of"
#
#     name = fields.Char(string="Name", required=True)
