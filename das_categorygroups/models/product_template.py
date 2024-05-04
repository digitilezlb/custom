from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # drinks_caption = fields.Char(string='Drinks Caption', default='Drinks', required=True, translate=True)
    drinks_ids = fields.Many2many(
        'product.product',  'drinks_product_related_rel',
        string='Drinks',
        domain="[('sale_ok', '=', True)]"
    )

    # sides_caption = fields.Char(string='Sides Caption', default='Sides', required=True, translate=True)

    sides_ids = fields.Many2many(
        'product.product',  'side_product_related_rel',
        string='Sides',
        domain="[('sale_ok', '=', True)]"
    )
    # related_caption = fields.Char(string='Related Caption', default='Related', required=True, translate=True)
    related_ids = fields.Many2many(
        'product.product','cat_product_related_rel',
        string='Related Products',
        domain="[('sale_ok', '=', True)]"
    )

    # liked_caption = fields.Char(string='Liked Caption', default='Liked', required=True, translate=True)
    liked_ids = fields.Many2many(
        'product.product', 'liked_product_related_rel',
        string='Liked Products',
        domain="[('sale_ok', '=', True)]"
    )

    # desserts_caption = fields.Char(string='Desserts Caption', default='Desserts', required=True, translate=True)
    desserts_ids = fields.Many2many(
        'product.product', 'desserts_product_related_rel',
        string='Desserts Products',
        domain="[('sale_ok', '=', True)]"
    )

    @api.onchange('categ_id')
    def fillproducts(self):
        try:
            if self.categ_id:

                self.drinks_ids = self.categ_id.drinks_ids


                self.sides_ids = self.categ_id.sides_ids


                self.related_ids = self.categ_id.related_ids


                self.liked_ids = self.categ_id.liked_ids

                self.desserts_ids = self.categ_id.desserts_ids
        except:
            pass

    # @api.onchange('drinks_ids')
    # def get_default_drink_domain(self):

    #     drinks = []
    #     for ingredient in self.drinks_ids:
    #         drinks.append(ingredient._origin.id)

    #     objects_to_remove = []

    #     for rem_ingredient in self.default_drink_id:
    #         if rem_ingredient._origin.id not in drinks:
    #             objects_to_remove.append(rem_ingredient)

    #     for obj in objects_to_remove:
    #         self.default_drink_id -= obj
    #
    # @api.onchange('sides_ids')
    # def get_default_sides_domain(self):

    #     sides = []
    #     for ingredient in self.sides_ids:
    #         sides.append(ingredient._origin.id)

    #     objects_to_remove = []

    #     for rem_ingredient in self.default_sides_id:
    #         if rem_ingredient._origin.id not in sides:
    #             objects_to_remove.append(rem_ingredient)

    #     for obj in objects_to_remove:
    #         self.default_sides_id -= obj