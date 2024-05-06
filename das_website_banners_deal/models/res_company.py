from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'


    deal_title1 = fields.Char(string="Deal Title1", translate=True)
    deal_title2 = fields.Char(string="Deal Title2", translate=True)
    deal_banner = fields.Image(string='Deal Banner')
    deal_banner_image_attachment = fields.Many2one('ir.attachment', compute="create_deal_banner_attachment_image", store=True)
    deal_background = fields.Image(string='Deal Background')
    deal_background_image_attachment = fields.Many2one('ir.attachment', compute="create_deal_background_attachment_image",
                                                   store=True)

    @api.depends('deal_banner')
    def create_deal_banner_attachment_image(self):
        for rec in self:
            if rec.deal_banner:
                rec.deal_banner_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.deal_title1) + " img",
                    'type': 'binary',
                    'datas': rec.deal_banner,
                    'store_fname': str(rec.deal_title1) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.deal_banner_image_attachment = image_att.id

    @api.depends('deal_background')
    def create_deal_background_attachment_image(self):
        for rec in self:
            if rec.deal_background:
                rec.deal_background_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.deal_title2) + " img",
                    'type': 'binary',
                    'datas': rec.deal_background,
                    'store_fname': str(rec.deal_title2) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.deal_background_image_attachment = image_att.id


