from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'



    is_add_ons = fields.Boolean(string="Add On Ingredient", default=False, readonly=False, store=True)

    product_addons_ids = fields.Many2many(
        'product.product',  # Model to relate with (itself in this case)
        'product_addons_rel',  # Name of the relationship table
        'product_id',  # Field name in the relationship table for the current record
        'addons_id',  # Field name in the relationship table for the related record
        string='Addons Ingredients',
        domain="[('is_add_ons', '=', True)]"
    )

    is_ingredient = fields.Boolean(string="Ingredient", default=False, store=True)

    is_combo = fields.Boolean(string="Combo", default=False, store=True)

    ingredient_ids = fields.Many2many(
        'product.product',  # Model to relate with (itself in this case)
        'product_ingredient_rel',  # Name of the relationship table
        'product_id',  # Field name in the relationship table for the current record
        'ingredient_id',  # Field name in the relationship table for the related record
        string='Ingredients',
        domain="[('is_ingredient', '=', True)]"
    )

    removable_ingredient_ids = fields.Many2many(
        'product.product',  # Model to relate with (itself in this case)
        'product_removable_ingredient_rel',  # Name of the relationship table
        'product_id',  # Field name in the relationship table for the current record
        'removable_ingredient_id',  # Field name in the relationship table for the related record
        string='Removable Ingredients',
        domain="[('id', 'in', ingredient_ids)]"
        # domain=lambda self: self._get_product_domain(),
        # domain="[('is_ingredient', '=', True)]"
    )

    content_ids = fields.Many2many(
        'product.product',  # Model to relate with (itself in this case)
        'product_content_rel',  # Name of the relationship table
        'product_id',  # Field name in the relationship table for the current record
        'content_id',  # Field name in the relationship table for the related record
        string='Contents',
        domain="[('is_ingredient', '!=', True),('is_add_ons', '!=', True)]"
    )


    name_ar = fields.Char(string='Name Ar')

    @api.onchange('ingredient_ids')
    def _get_product_domain(self):

        ingredients = []
        for ingredient in self.ingredient_ids:
            ingredients.append(ingredient._origin.id)


        objects_to_remove = []

        for rem_ingredient in self.removable_ingredient_ids:
            if rem_ingredient._origin.id not in ingredients:
                objects_to_remove.append(rem_ingredient)

        for obj in objects_to_remove:
            self.removable_ingredient_ids -= obj