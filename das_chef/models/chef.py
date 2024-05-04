from odoo import api, fields, models, _
from datetime import datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta



class Chef(models.Model):
    _inherit = 'res.partner'
    _description = 'inherit Contacts'


    kitchen_id = fields.Many2one('digitile.kitchen', string="Kitchen",
                                 domain=lambda self: self._get_domain_for_custom_field())

    is_chef = fields.Boolean(string='Is Chef', default=False)
    
    def _get_domain_for_custom_field(self):
        company_id = self.env.company.id
        domain = [('company_id', '=', company_id)]
        return domain
        
    # @api.model
    # def create(self, vals):
    #
    #     if 'is_chef' in vals:
    #
    #         if vals['is_chef'] == True:
    #
    #             if vals['kitchen_id'] == False:
    #                 raise ValidationError(_('Choose Your Kitchen !'))
    #
    #     result = super().create(vals)
    #     return result



    # def write(self, vals):
    #
    #     if self.is_chef == True:
    #         if 'kitchen_id' in vals:
    #             if vals['kitchen_id'] == False:
    #                 raise ValidationError(_('Choose Your Kitchen !'))
    #     res = super().write(vals)
    #     return res

    
