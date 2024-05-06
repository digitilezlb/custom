from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):

        result = []
        name = ''
        for contact in self:
            if contact.parent_id:
                name = 'TEST'

            # if contact.country_id:
            #     name = contact.country_id.name
            # if contact.city_id:
            #     if name !='':
            #         name = name + ' ' + contact.city_id.name
            #     else:
            #         name = contact.city_id.name
            # if contact.street2:
            #     if name != '':
            #         name = name + ' ' + contact.street2
            #     else:
            #         name = contact.street2
            # if name != '':
            #     name = name + ' ' + contact.name
            else:
                name = contact.name
            result.append((contact.id, name))
        return result