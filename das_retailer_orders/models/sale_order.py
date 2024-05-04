from odoo import api, fields, models
from datetime import date, datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    app_record = fields.Boolean()

    def get_retailer_price(self, product_id):
        product = self.env['product.template'].sudo().search(
            [('id', '=', product_id)])

        retailer_price_list = self.env['product.pricelist'].sudo().search(
            [('retailer_price_list', '=', True), ('set_as_retailer_price_list', '=', True)])

        shelf_price = product.list_price

        for line in retailer_price_list.item_ids:
            if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
                retailer_price = shelf_price - (
                        (line.percent_price / 100) * shelf_price)
            elif line.applied_on == '2_product_category':
                category_id = self.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                products_ids = self.env['product.template'].sudo().search(
                    [('categ_id', '=', category_id.id)])
                if product in products_ids:
                    retailer_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
            elif line.applied_on == '3_global':
                retailer_price = shelf_price - (
                        (line.percent_price / 100) * shelf_price)

        # wassim 10-08-2023
        try:
            if retailer_price:
                price = retailer_price
            else:
                price = shelf_price
        except:
            price = shelf_price

        return price

    def get_24h_deal_price(self, product_id):
        product = self.env['product.template'].sudo().search(
            [('id', '=', product_id)])

        date = datetime.today().date()
        today_pricelist = self.env['product.pricelist'].sudo().search(
            [('from_date', '=', date), ('hours_24_deal', '=', True)])

        shelf_price = product.list_price
        deal_price = False

        if today_pricelist:
            for line in today_pricelist.item_ids:
                if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
                    deal_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '2_product_category':
                    category_id = self.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                    products_ids = self.env['product.template'].sudo().search(
                        [('categ_id', '=', category_id.id)])
                    if product in products_ids:
                        deal_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '3_global':
                    deal_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
        return deal_price

    def get_promotion_price(self, product_id):
        product = self.env['product.template'].sudo().search(
            [('id', '=', product_id)])

        published_promotions = self.env['product.pricelist'].sudo().search(
            [('is_published', '=', True), ('is_promotion', '=', True)])

        shelf_price = product.list_price
        promotion_price = False

        if published_promotions:
            for line in published_promotions.item_ids:
                if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
                    promotion_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '2_product_category':
                    category_id = self.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                    products_ids = self.env['product.template'].sudo().search(
                        [('categ_id', '=', category_id.id)])
                    if product in products_ids:
                        promotion_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '3_global':
                    promotion_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
        return promotion_price

    def get_add_price(self, product_id):
        product = self.env['product.template'].sudo().search(
            [('id', '=', product_id)])

        published_ad = self.env['product.pricelist'].sudo().search(
            [('is_ad', '=', True), ('is_set_as_ad', '=', True)])

        shelf_price = product.list_price
        add_price = False

        if published_ad:
            for line in published_ad.item_ids:
                if line.applied_on == '1_product' and line.product_tmpl_id.id == product.id:
                    add_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '2_product_category':
                    category_id = self.env['product.category'].sudo().search([('id', '=', line.categ_id.id)])
                    products_ids = self.env['product.template'].sudo().search(
                        [('categ_id', '=', category_id.id)])
                    if product in products_ids:
                        add_price = shelf_price - (
                                (line.percent_price / 100) * shelf_price)
                elif line.applied_on == '3_global':
                    add_price = shelf_price - (
                            (line.percent_price / 100) * shelf_price)
        return add_price

    def get_promo_price(self, product_id):
        if self.get_24h_deal_price(product_id):
            price = self.get_24h_deal_price(product_id)
        elif self.get_promotion_price(product_id):
            price = self.get_promotion_price(product_id)
        elif self.get_add_price(product_id):
            price = self.get_add_price(product_id)
        else:
            price = self.get_retailer_price(product_id)
        return price

    def get_updated_price(self):
        for line in self.order_line:
            line.price_unit = self.get_promo_price(line.product_id.product_tmpl_id.id)

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        self.get_updated_price()
        return result
