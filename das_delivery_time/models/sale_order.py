from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    zone_id = fields.Many2one('zone.zone', string="zone", required=False,domain=lambda self: self._get_domain())


    def _get_domain(self):

        company_id = self.env.company.id
        domain = [('company_id', '=', company_id)]
        return domain
