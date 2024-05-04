from odoo import api, fields, models, exceptions

class OrderKitchen(models.Model):
    _name = 'digitile.kitchen'
    _description = 'digitile.kitchen'

    name = fields.Char(string='name',required=True, translate=True)

    company_id = fields.Many2one('res.company', string="Company", required=True)
    default_kitchen = fields.Boolean(string="Set as Default", default=False, readonly=True, store=True)
    product_ids = fields.One2many('product.template', 'kitchen_id', string='Products')
    _sql_constraints = [
        ('unique_name_company', 'unique(name, company_id)', 'Kitchen name must be unique per company.'),
    ]

    ready_kitchen = fields.Boolean(string="Set as Ready", default=False, readonly=True, store=True)

    # , ('unique_name', 'unique(name)', 'Kitchen name must be unique.'),
    
    def set_as_default(self):


        for rec in self:
            all_ads = rec.env['digitile.kitchen'].sudo().search([('company_id','=',self.company_id.id)])
            for ad in all_ads:
                ad.default_kitchen = False
            rec.default_kitchen = True

    def un_set_default(self):

        for rec in self:
            all_ads = rec.env['digitile.kitchen'].sudo().search([('company_id', '=', self.company_id.id)])
            for ad in all_ads:
                ad.default_kitchen = False
            # rec.default_kitchen = True

    def set_as_ready(self):

        for rec in self:
            all_ads = rec.env['digitile.kitchen'].sudo().search([('company_id', '=', self.company_id.id)])
            for ad in all_ads:
                ad.ready_kitchen = False
            rec.ready_kitchen = True

    def un_set_ready(self):

        for rec in self:
            all_ads = rec.env['digitile.kitchen'].sudo().search([('company_id', '=', self.company_id.id)])
            for ad in all_ads:
                ad.ready_kitchen = False
            # rec.ready_kitchen = True

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    kitchen_id = fields.Many2one('digitile.kitchen', string='Kitchen', ondelete='restrict',domain=lambda self: self._get_domain_for_custom_field())
    preparing_time = fields.Selection(string="Preparing Time in minutes",
                                              selection =[("0", ""),
                                                ("10", "10 mins"),
                                                ("20", "20 mins"),
                                                ("30", "30 mins"),
                                                ("40", "40 mins"),
                                                ("50", "50 mins"),
                                                ("60", "60 mins"),
                                                ("70", "70 mins"),
                                                ("80", "80 mins"),
                                                ("90", "90 mins"),
                                                ("100", "100 mins"),
                                                ("110", "110 mins"),
                                                ("120", "120 mins"),
                                               ],  store=True,
                                    readonly= False)
                                    
    def _get_domain_for_custom_field(self):

        company_id = self.env.company.id
        domain = [('company_id', '=', company_id)]

        return domain