from odoo import fields, models, api


class MainPageSection(models.Model):
    _name = 'main.page.section'
    _description = 'main.page.section'

    name = fields.Char(string='name', required=True, translate=True)


    product_ids = fields.Many2many(
        'product.template',  # Model to relate with (itself in this case)
        # 'product_main_page_section_rel',  # Name of the relationship table
        # 'main_page_section_id',  # Field name in the relationship table for the current record
        # 'product_id',  # Field name in the relationship table for the related record
        string='Products',
        domain="[('app_publish','=',True),('company_id', 'in', [company_id,False])]"
        # domain="[('company_id', '=?', company_id),'|', ('company_id', '=', False)]"
        # domain=lambda self: self._get_product_domain(),
        # domain="[('is_ingredient', '=', True)]"

    )

    # section_number = fields.Integer(string='Number', required=True)
    section_number = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ], string='Number', required=True, default='1')

    main_page_section_banner = fields.Image(string='Main Page Section Banner')
    main_page_section_image_attachment = fields.Many2one('ir.attachment',
                                                         compute="create_main_page_section_attachment_image",
                                                         store=True)
    company_id = fields.Many2one('res.company', string="company",default= lambda self: self._get_default_value(),store=True, required=False,readonly=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Name must be unique.'),
    ]

    def _get_default_value(self):

        company_id = self.env.company.id

        return company_id

    def _get_domain_for_custom_field(self):

        company_id = self.env.company.id
        domain = [('company_id', 'in', [company_id,False])]

        return domain

    @api.depends('main_page_section_banner')
    def create_main_page_section_attachment_image(self):
        for rec in self:
            if rec.main_page_section_banner:
                rec.main_page_section_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.main_page_section_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'main.page.section',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.main_page_section_image_attachment = image_att.id

