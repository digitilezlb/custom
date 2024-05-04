from odoo import api, fields, models, _, exceptions

from datetime import datetime
class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    user_owner = fields.Boolean(string="user_owner", default=False, store=True)

    def unlink(self):
        for rec in self:
            if rec.user_owner:
                raise exceptions.UserError("You can't delete this user")
        return super(ResUsers, self).unlink()

    def force_log_out(self):
        user = self.env["res.users"].sudo().search([("id", "=", self.id)])
        try:
            if user:
                user.write({
                    'is_log_in': False,
                    'log_time': datetime.now()
                })
                return self.get_message()
        except:
            raise exceptions.UserError("Error!!!")


    def get_message(self):
        # print('--------------------------------------------------------------------')
        view = self.env.ref('das_sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = "Logout Done!"
        return {
            'name': 'Success!',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context, }

