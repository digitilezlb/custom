from odoo import api, fields, models, _, exceptions


class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    user_admin = fields.Boolean(string="user_admin", default=False, store=True)

    def unlink(self):
        for rec in self:
            if rec.user_admin:
                raise exceptions.UserError("You can't delete this user")
        return super(ResUsers, self).unlink()

    def write(self,vals):
        for rec in self:
            if 'name' in vals:
                if rec.name == 'Administrator' or rec.name== 'Admin' or rec.name == 'administrator' or rec.name == 'admin':
                    raise exceptions.UserError("You can't change the name of this user")
        res = super().write(vals)
        return res