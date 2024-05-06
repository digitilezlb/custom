from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    is_cv = fields.Boolean()
    image = fields.Image(string="Image")
    image_attachment = fields.Many2one('ir.attachment', compute="create_image_attachment",
                                                 store=True)

    @api.depends('image')
    def create_image_attachment(self):
        for rec in self:
            if rec.image:
                rec.image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'hr.job',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.image_attachment = image_att.id