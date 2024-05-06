from odoo import api, fields, models, exceptions

class Team(models.Model):
    _name = "team"
    _description = "team"

    name = fields.Char(string='Name',required=True, translate=True)

    team_image = fields.Image(string="Image")
    team_image_attachment = fields.Many2one('ir.attachment', compute="create_team_image_attachment_image",
                                                 store=True)

    team_member = fields.Many2many(
        'res.partner','team_team_member_rel',
        string='Members', domain="[('is_member', '=', True)]"
    )
    
    company_id = fields.Many2one('res.company', string="company", required=False)

    @api.depends('team_image')
    def create_team_image_attachment_image(self):
        for rec in self:
            if rec.team_image:
                rec.team_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.team_image,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'team',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.team_image_attachment = image_att.id



    # @api.model
    # def create(self, vals):
    #     existing_record = self.search([])
    #     if existing_record:
    #         raise exceptions.UserError("Only one 'Team' record is allowed.")
    #     return super(Team, self).create(vals)