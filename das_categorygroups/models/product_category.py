from odoo import api, fields, models


class CategoryAdds(models.Model):
    _inherit = 'product.category'

    drinks_ids = fields.Many2many(
        'product.product',  # Field name in the relationship table for the related record
        string='Drinks',
        domain="[('sale_ok', '=', True)]"
    )

    sides_ids = fields.Many2many(
        'product.product',  'side_related_rel',
        string='Sides',
        domain="[('sale_ok', '=', True)]"
    )

    related_ids = fields.Many2many(
        'product.product','cat_related_rel',
        string='Related Products',
        domain="[('sale_ok', '=', True)]"
    )

    liked_ids = fields.Many2many(
        'product.product', 'liked_related_rel',
        string='Liked Products',
        domain="[('sale_ok', '=', True)]"
    )

    desserts_ids = fields.Many2many(
        'product.product', 'desserts_related_rel',
        string='Desserts Products',
        domain="[('sale_ok', '=', True)]"
    )
    
    company_id = fields.Many2one('res.company', string="company", required=False)
