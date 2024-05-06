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
            menus.discard(self.env.ref("sale.menu_sale_config").id)
        except:
            pass

        try:
            menus.discard(self.env.ref("sale.menu_sale_invoicing").id)
        except:
            pass

        try:
            menus.discard(self.env.ref("sale.report_sales_team").id)
        except:
            pass


        try:
            menus.discard(self.env.ref("website_sale.menu_catalog_pricelists").id)
        except:
            pass

        try:
            menus.discard(self.env.ref("das_template_settings.team_menu_item").id)
        except:
            pass

        try:
            #menu from stock === Inventory
            menus.discard(self.env.ref("stock.menu_stock_root").id)
            # menus.discard(self.env.ref("stock.stock_picking_type_menu").id)
            # menus.discard(self.env.ref("stock.menu_stock_warehouse_mgmt").id)
            # menus.discard(self.env.ref("stock.menu_warehouse_report").id)
            # menus.discard(self.env.ref("stock.menu_warehouse_report").id)
            # menus.discard(self.env.ref("stock.menu_stock_general_settings").id)
            # menus.discard(self.env.ref("stock.menu_pickingtype").id)
            # menus.discard(self.env.ref("stock.menu_reordering_rules_config").id)
            # menus.discard(self.env.ref("stock.menu_warehouse_config").id)
            # menus.discard(self.env.ref("stock.menu_wms_barcode_nomenclature_all").id)


        except:
            pass

        try:
            menus.discard(self.env.ref("mrp.menu_mrp_root").id)
        except:
            pass

        try:
            'Email Marketing'
            menus.discard(self.env.ref("mass_mailing.mass_mailing_menu_root").id)
        except:
            pass

        try:
            'EMployees'
            menus.discard(self.env.ref("hr.menu_hr_root").id)
        except:
            pass
        try:
            'fleet'
            menus.discard(self.env.ref("fleet.menu_root").id)
        except:
            pass

        try:
            'link tracker'
            menus.discard(self.env.ref("utm.menu_link_tracker_root").id)
        except:
            pass
        try:
            'Invoicing'
            menus.discard(self.env.ref("account.menu_finance").id)
        except:
            pass



        try:
            'Website'
            menus.discard(self.env.ref("website.menu_website_configuration").id)
        except:
            pass

        # try:
        #     'Apps'
        #     menus.discard(self.env.ref("base.menu_management").id)
        # except:
        #     pass


        return menus