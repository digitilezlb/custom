from odoo import api, fields, models, _, exceptions
import requests
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    def write(self, vals):
        if 'name' in vals:
            if self.id == 2:
                raise ValidationError(_("You can't change the name of this user"))
        return super(ResUsers, self).write(vals)

    def unlink(self):
        if self.id == 2:
            raise ValidationError("You can't delete this user")
        return super(ResUsers, self).unlink()

class ChangePasswordUser(models.TransientModel):
    """ A model to configure users in the change password wizard. """
    _inherit = 'change.password.user'
    _description = 'User, Change Password Wizard '

    def change_password_button(self):

        for line in self:

            if line.user_id.id == 2:
                raise ValidationError(_("You can't change the password of this user."))

            if not line.new_passwd:
                raise ValidationError(_("Before clicking on 'Change Password', you have to write a new password."))

            line.user_id._change_password(line.new_passwd)

        # don't keep temporary passwords in the database longer than necessary
        self.write({'new_passwd': False})


