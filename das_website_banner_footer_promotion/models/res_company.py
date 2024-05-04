from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'

    promotion_title = fields.Char(string="Promotion Title", translate=True)
    promotion_banner = fields.Image(string='Promotion Banner')
    promotion_image_attachment = fields.Many2one('ir.attachment', compute="create_promotion_attachment_image", store=True)

    footer_banner = fields.Image(string='Footer Banner')
    footer_image_attachment = fields.Many2one('ir.attachment', compute="create_footer_image_attachment",
                                                 store=True)

    @api.depends('promotion_banner')
    def create_promotion_attachment_image(self):
        for rec in self:
            if rec.promotion_banner:
                rec.promotion_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.promotion_title) + " img",
                    'type': 'binary',
                    'datas': rec.promotion_banner,
                    'store_fname': str(rec.promotion_title) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.promotion_image_attachment = image_att.id

    @api.depends('footer_banner')
    def create_footer_image_attachment(self):
        for rec in self:
            if rec.footer_banner:
                rec.footer_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.promotion_title) + " img1",
                    'type': 'binary',
                    'datas': rec.footer_banner,
                    'store_fname': str(rec.promotion_title) + "img1",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.footer_image_attachment = image_att.id