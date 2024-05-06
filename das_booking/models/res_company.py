from odoo import fields, models,api


class Company(models.Model):
    _inherit = 'res.company'
    _description = 'res.company'

    booking_title = fields.Char(string="Booking Title")
    booking_banner = fields.Image(string='Booking Banner')
    booking_image_attachment = fields.Many2one('ir.attachment', compute="create_booking_attachment_image", store=True)



    @api.depends('booking_banner')
    def create_booking_attachment_image(self):
        for rec in self:
            if rec.booking_banner:
                rec.booking_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.booking_title) + " img",
                    'type': 'binary',
                    'datas': rec.booking_banner,
                    'store_fname': str(rec.booking_title) + "img",
                    'res_model': 'res.company',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.booking_image_attachment = image_att.id