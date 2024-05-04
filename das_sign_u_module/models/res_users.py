from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_credentials_api(self, password, env, user_id):
        assert password
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [user_id]
        )
        [hashed] = self.env.cr.fetchone()
        valid, replacement = self._crypt_context() \
            .verify_and_update(password, hashed)
        status = 1
        if replacement is not None:
            self._set_encrypted_password(user_id, replacement)
            status = True
        if not valid:
            status = False
        return status