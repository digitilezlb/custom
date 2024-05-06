from odoo import api, fields, models, exceptions

class TeamMember(models.Model):

    _inherit = 'res.partner'
    _description = "member"
    position = fields.Char(string='Position', translate=True)
    is_member = fields.Boolean(string='Is Member', default=False)
    team_member_image_attachment = fields.Many2one('ir.attachment', compute="create_team_member_image_attachment_image",
                                            store=True)

    @api.depends('image_1920')
    def create_team_member_image_attachment_image(self):

        for rec in self:
            if rec.image_1920:
                rec.team_member_image_attachment.unlink()
                image_att = rec.env['ir.attachment'].sudo().create({
                    'name': str(rec.name) + " img",
                    'type': 'binary',
                    'datas': rec.image_1920,
                    'store_fname': str(rec.name) + "img",
                    'res_model': 'team',
                    'res_id': rec.id,
                    'public': True
                })
                if image_att:
                    rec.team_member_image_attachment = image_att.id

    # @api.model
    # def create(self, vals):
    #     self.is_member = True
    #     vals['is_member'] = True
    #     return super(TeamMember, self).create(vals)