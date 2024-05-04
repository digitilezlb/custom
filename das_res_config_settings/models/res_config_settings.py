# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    fire_base_api_key = fields.Char(
        string='Fire Base Api Key',
        config_parameter='das_res_config_settings.fire_base_api_key')


            
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('das_res_config_settings.fire_base_api_key',
                                                         self.fire_base_api_key)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        privacy_pol = ICPSudo.get_param('das_res_config_settings.fire_base_api_key')

        res.update(
            fire_base_api_key=privacy_pol
        )
        return res
