from odoo import api, fields, models, _,tools
import json
from odoo import http
from odoo.http import request

class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        try:
            menus.discard(self.env.ref("sale.menu_product_pricelist_main").id)
        except:
            pass
        try:
            menus.discard(self.env.ref("website_sale.menu_catalog_pricelists").id)
        except:
            pass

        return menus