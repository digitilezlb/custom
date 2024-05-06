from odoo import fields, models, api


class DasMenuType(models.Model):
    _name = 'das.menu.type'
    _description = 'das.menu.type'

    name = fields.Char(string='name', required=True, translate=True)

class DasMenu(models.Model):
    _name = 'das.menu'
    _description = 'das.menu'

    name = fields.Char(string='name', required=True, translate=True)
    type_id = fields.Many2one('das.menu.type', string="Type", required=True)
    is_web_menu = fields.Boolean("Website Menu")
    qr_code = fields.Char(string='Qr code', required=True)
    categories = fields.One2many('das.category.menu', 'menu_id',
                                 string='Categories', copy=True)
    company_id = fields.Many2one('res.company', string="Company", required=False,readonly=True,
                                 default=lambda self: self._get_default_value())
    menu_banner = fields.Image(string='Menu Banner')
    menu_image_attachment = fields.Many2one('ir.attachment',
                                            compute="create_menu_attachment_image",
                                            store=True)


    def _get_default_value(self):
        company_id = self.env.company.id
        return company_id

    def set_as_web_menu(self):
        for rec in self:
            all_ads = rec.env['das.menu'].sudo().search([('company_id', '=', self.company_id.id)])
            for ad in all_ads:
                ad.is_web_menu = False
            rec.is_web_menu = True
    @api.depends('menu_banner')
    def create_menu_attachment_image(self):
        for rec in self:
            if rec.menu_banner:
                rec.menu_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.menu_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'das.menu',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.menu_image_attachment = image_att.id


class DasCategoryMenu(models.Model):
    _name = 'das.category.menu'
    _description = 'das.category.menu'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index='trigram',translate=True, required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,translate=True,
        store=True)
    parent_id = fields.Many2one('das.category.menu', 'Parent Category', index=True, ondelete='cascade',domain="[('menu_id','=',menu_id)]")
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many('das.category.menu', 'parent_id', 'Child Categories')

    menu_id = fields.Many2one('das.menu', string='Menu', index=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string="company", required=False,default=lambda self: self._get_default_value())
    product_ids = fields.Many2many(
        'product.product',  # Model to relate with (itself in this case)
        'product_category_menu_rel',  # Name of the relationship table
        'category_menu_id',  # Field name in the relationship table for the current record
        'product_id',  # Field name in the relationship table for the related record
        string='Products',
        # domain="[('company_id', '=?', company_id),'|', ('company_id', '=', False)]"
        domain="[('app_publish','=',True),('company_id', 'in', [company_id,False])]"
    )

    category_menu_banner = fields.Image(string='category Banner')
    category_menu_image_attachment = fields.Many2one('ir.attachment',
                                                     compute="create_category_menu_attachment_image",
                                                     store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):

        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super().name_get()

    # @api.ondelete(at_uninstall=False)
    # def _unlink_except_default_category(self):
    #     main_category = self.env.ref('product.product_category_all', raise_if_not_found=False)
    #     if main_category and main_category in self:
    #         raise UserError(_("You cannot delete this product category, it is the default generic category."))
    #     expense_category = self.env.ref('product.cat_expense', raise_if_not_found=False)
    #     if expense_category and expense_category in self:
    #         raise UserError(_("You cannot delete the %s product category.", expense_category.name))
    def _get_default_value(self):
        company_id = self.env.company.id
        return company_id

    def _get_product_domain(self):

        domain = ['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)]

        return domain

    @api.depends('category_menu_banner')
    def create_category_menu_attachment_image(self):
        for rec in self:
            if rec.category_menu_banner:
                rec.category_menu_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.category_menu_banner,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'das.menu',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.category_menu_image_attachment = image_att.id
