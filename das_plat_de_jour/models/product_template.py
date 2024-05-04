from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'product.template'


    is_plat_de_jour = fields.Boolean(string="Plat Du Jour" )

