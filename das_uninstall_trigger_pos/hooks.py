from odoo import api,SUPERUSER_ID

def test_uninstall_hook(cr ,registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("""
               DROP TRIGGER IF EXISTS add_pos_to_digitile_order_trigger ON pos_order;
           """)
    env.cr.execute("""
               DROP FUNCTION IF EXISTS trigger_add_pos_to_digitile_order_function() CASCADE;
           """)

    env.cr.execute("""
                       DROP TRIGGER IF EXISTS update_pos_to_digitile_order_trigger ON pos_order;
                   """)
    env.cr.execute("""
                       DROP FUNCTION IF EXISTS trigger_Update_pos_to_digitile_order_function() CASCADE;
                   """)

    env.cr.execute("""
                               DROP TRIGGER IF EXISTS update_pos_to_pos_order_trigger ON digitile_order_kitchen;
                           """)
    env.cr.execute("""
                               DROP FUNCTION IF EXISTS trigger_Update_pos_to_pos_order_function() CASCADE;
                           """)

    env.cr.execute("""
                           DROP TRIGGER IF EXISTS add_pos_to_order_line_trigger ON pos_order_line;
                       """)
    env.cr.execute("""
                           DROP FUNCTION IF EXISTS trigger_add_pos_to_order_line_function() CASCADE;
                       """)

    env.cr.execute("""
                                   DROP TRIGGER IF EXISTS update_pos_to_digitile_pos_order_line_trigger ON pos_order_line;
                               """)
    env.cr.execute("""
                                   DROP FUNCTION IF EXISTS trigger_Update_pos_to_order_line_function() CASCADE;
                               """)

    env.cr.execute("""
                                           DROP TRIGGER IF EXISTS update_pos_to_pos_order_line_trigger ON digitile_order_kitchen_line;
                                       """)
    env.cr.execute("""
                                           DROP FUNCTION IF EXISTS trigger_Update_pos_to_pos_order_line_function() CASCADE;
                                       """)

    env.cr.execute("""
                                                   DROP TRIGGER IF EXISTS delete_pos_order_line_trigger ON pos_order_line;
                                               """)
    env.cr.execute("""
                                                   DROP FUNCTION IF EXISTS trigger_Delete_pos_order_line_function() CASCADE;
                                               """)