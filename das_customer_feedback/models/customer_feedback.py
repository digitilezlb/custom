from odoo import fields, models, api


class CustomerFeedback(models.Model):
    _name = 'customer.feedback'
    _description = 'customer.feedback'

    name = fields.Char(string='Customer Name',required=True, translate=True)
    customer_image = fields.Image('Image')
    customer_image_attachment = fields.Many2one('ir.attachment', compute="create_customer_image_attachment", store=True)
    customer_comment = fields.Text(string='Comment', translate=True)
    company_id = fields.Many2one('res.company', string="company", required=False)
    
    @api.depends('customer_image')
    def create_customer_image_attachment(self):
        for rec in self:
            if rec.customer_image:
                rec.customer_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.customer_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'customer.feedback',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.customer_image_attachment = image_att.id