from odoo import api, fields, models, exceptions

class AboutUsVision(models.Model):
    _name = "about.us.vision"
    _description = "about.us.vision"

    name = fields.Char(string='Name',required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    about_us_vision_image = fields.Image(string="Image")
    about_us_vision_image_attachment = fields.Many2one('ir.attachment', compute="create_about_us_vision_image_attachment_image",
                                                 store=True)

    company_id = fields.Many2one('res.company', string="company", required=False)
    
    @api.depends('about_us_vision_image')
    def create_about_us_vision_image_attachment_image(self):
        for rec in self:
            if rec.about_us_vision_image:
                rec.about_us_vision_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.about_us_vision_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'about.us',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.about_us_vision_image_attachment = image_att.id


    # @api.model
    # def create(self, vals):
    #     existing_record = self.search([])
    #     if existing_record:
    #         raise exceptions.UserError("Only one 'About Us Vision' record is allowed.")
    #     return super(AboutUsVision, self).create(vals)