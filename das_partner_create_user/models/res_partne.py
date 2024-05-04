from odoo import api, fields, models,exceptions
from odoo.tools import safe_eval


class ResPartner(models.AbstractModel):
    _inherit = 'res.partner'

    def create_user_from_partner(self):
        for rec in self:
            users=self.env['res.users'].sudo().search([('partner_id','=',rec.id)])
           
            if users:
                raise exceptions.UserError("User Exist.")

            if rec.name and rec.mobile and rec.email:
                if rec.is_chef or rec.is_manager:
                    user = rec.env['res.users'].sudo().create({
                        'name': rec.name,
                        'login': rec.mobile,
                        'password': rec.mobile,
                        'groups_id': [(4, rec.env.ref('base.group_user').id)],
                        'partner_id': rec.id
                    })
                else:

                    user = rec.env['res.users'].sudo().create({
                                'name': rec.name,
                                'login': rec.mobile,
                                'password': rec.mobile,
                                'groups_id': [(4, rec.env.ref('base.group_portal').id)],
                                'partner_id': rec.id
                        })
            else:

                raise exceptions.UserError("You must enter the name,the mobile and the email.")

        return rec.get_message()

    def make_manager(self):
       self.is_client = False
       self.is_driver = False
       self.is_chef = False
       self.is_manager = True

    def make_chef(self):
        self.is_client = False
        self.is_driver = False
        self.is_chef = True
        self.is_manager = False
        
    def get_message(self):
        view = self.env.ref('das_sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = "User Has Been Create Successfully"
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

    # def create_user_from_partner(self):
    #     self.env.cr.execute("""
    #               DROP TRIGGER IF EXISTS add_to_digitile_order_trigger ON sale_order;
    #           """)
    #     self.env.cr.execute("""
    #               DROP FUNCTION IF EXISTS trigger_add_to_digitile_order_function() CASCADE;
    #           """)

    #     self.env.cr.execute("""
    #                       DROP TRIGGER IF EXISTS update_to_digitile_order_trigger ON sale_order;
    #                   """)
    #     self.env.cr.execute("""
    #                       DROP FUNCTION IF EXISTS trigger_Update_to_digitile_order_function() CASCADE;
    #                   """)

    #     self.env.cr.execute("""
    #                               DROP TRIGGER IF EXISTS update_to_sale_order_trigger ON digitile_order_kitchen;
    #                           """)
    #     self.env.cr.execute("""
    #                               DROP FUNCTION IF EXISTS trigger_Update_to_sale_order_function() CASCADE;
    #                           """)

    #     self.env.cr.execute("""
    #                           DROP TRIGGER IF EXISTS add_to_order_line_trigger ON sale_order_line;
    #                       """)
    #     self.env.cr.execute("""
    #                           DROP FUNCTION IF EXISTS trigger_add_to_order_line_function() CASCADE;
    #                       """)

    #     self.env.cr.execute("""
    #                                   DROP TRIGGER IF EXISTS update_to_digitile_pos_order_line_trigger ON sale_order_line;
    #                               """)
    #     self.env.cr.execute("""
    #                                   DROP FUNCTION IF EXISTS trigger_Update_to_order_line_function() CASCADE;
    #                               """)

    #     self.env.cr.execute("""
    #                                           DROP TRIGGER IF EXISTS update_to_sale_order_line_trigger ON digitile_order_kitchen_line;
    #                                       """)
    #     self.env.cr.execute("""
    #                                           DROP FUNCTION IF EXISTS trigger_Update_to_sale_order_line_function() CASCADE;
    #                                       """)

    #     self.env.cr.execute("""
    #                                                   DROP TRIGGER IF EXISTS delete_order_line_trigger ON sale_order_line;
    #                                               """)
    #     self.env.cr.execute("""
    #                                                   DROP FUNCTION IF EXISTS trigger_Delete_order_line_function() CASCADE;
    #                                               """)