from odoo import fields, models, api


class PlatDeJour(models.Model):
    _name = 'plat.de.jour'
    _description = 'plat.de.jour'

    name = fields.Char(string='name', required=True, translate=True)

    create_uid = fields.Integer(string='create_uid')
    write_uid = fields.Integer(string='write_uid')
    product_ids = fields.Many2many(
        'product.template',  # Model to relate with (itself in this case)
        'product_plat_de_jour_rel',  # Name of the relationship table
        'plat_de_jour_id',  # Field name in the relationship table for the current record
        'product_id',  # Field name in the relationship table for the related record
        string='Products',
        domain="['|', ('company_id', '=', False),('company_id', '=?', company_id),('is_plat_de_jour','=',True)]"

    )


    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day', required=True, default='0')

    # _sql_constraints = [
    #     ('unique_day_of_week', 'unique(day_of_week)', 'Day must be unique.'),
    # ]

    _sql_constraints = [
        ('unique_day_of_week_company', 'unique(day_of_week, company_id)', 'Day of week and company must be unique.'),
    ]
    # _sql_constraints = [
    #     ('unique_day_of_week_company', 'unique(day_of_week, company_id) WHERE company_id IS NOT NULL',
    #      'Day of week and company must be unique.'),
    # ]
    
    plat_de_jour_banner = fields.Image(string='Plat De Jour Banner')
    plat_de_jour_image_attachment = fields.Many2one('ir.attachment',
                                                         compute="create_plat_de_jour_attachment_image",
                                                         store=True)
    company_id = fields.Many2one('res.company', string="company", required=False,store=True,readonly=False,default= lambda self: self._get_default_value())

    def _get_default_value(self):

        company_id = self.env.company.id

        return company_id
    def _get_domain_for_custom_field(self):

        company_id = self.env.company.id
        domain = [('company_id', 'in', [company_id,False]),('is_plat_de_jour','=',True)]

        return domain
    @api.depends('plat_de_jour_banner')
    def create_plat_de_jour_attachment_image(self):
        for rec in self:
            if rec.plat_de_jour_banner:
                rec.plat_de_jour_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.plat_de_jour_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'plat.de.jour',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.plat_de_jour_image_attachment = image_att.id

