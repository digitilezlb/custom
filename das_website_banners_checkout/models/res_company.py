from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'


    checkout_title = fields.Char(string="Checkout Title", translate=True)
    checkout_banner = fields.Image(string='Checkout Banner')
    checkout_image_attachment = fields.Many2one('ir.attachment', compute="create_checkout_attachment_image", store=True)

    @api.depends('checkout_banner')
    def create_checkout_attachment_image(self):
        for rec in self:
            if rec.checkout_banner:
                rec.checkout_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.checkout_title) + " img",
                    'type': 'binary',
                    'datas': rec.checkout_banner,
                    'store_fname': str(rec.checkout_title) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.checkout_image_attachment = image_att.id

