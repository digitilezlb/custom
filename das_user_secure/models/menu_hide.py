from odoo import api, models, tools


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        # print('---------------- self.env.user.user_admin-----------------', self.env.user.user_admin)
        menus = super(Menu, self)._visible_menu_ids(debug)

        if 'Administrator' not in self.env.user.name and 'administrator' not in self.env.user.name:
        # if not self.env.user.user_admin:

            menus.discard(self.env.ref("base.menu_action_res_users").id)
            'Apps'
            menus.discard(self.env.ref("base.menu_management").id)
            menus.discard(self.env.ref("base.menu_administration").id)
        return menus

        # def _visible_menu_ids(self, debug=False):
        #
        #     menus = super(Menu, self)._visible_menu_ids(debug)
        #     if 'Administrator' not in self.env.user.name:
        #         menus.discard(self.env.ref("base.menu_action_res_users").id)
        #         # 'Apps'
        #         # menus.discard(self.env.ref("base.menu_management").id)
        #         # menus.discard(self.env.ref("base.menu_administration").id)
        #     return menus
