from odoo import api,SUPERUSER_ID

def test_uninstall_hook(cr ,registry):

    env = api.Environment(cr,SUPERUSER_ID,{})
    env.cr.execute("""
           DROP TRIGGER IF EXISTS add_to_digitile_order_trigger ON sale_order;
       """)
    env.cr.execute("""
           DROP FUNCTION IF EXISTS trigger_add_to_digitile_order_function() CASCADE;
       """)

    env.cr.execute("""
                   DROP TRIGGER IF EXISTS update_to_digitile_order_trigger ON sale_order;
               """)
    env.cr.execute("""
                   DROP FUNCTION IF EXISTS trigger_Update_to_digitile_order_function() CASCADE;
               """)

    env.cr.execute("""
                           DROP TRIGGER IF EXISTS update_to_sale_order_trigger ON digitile_order_kitchen;
                       """)
    env.cr.execute("""
                           DROP FUNCTION IF EXISTS trigger_Update_to_sale_order_function() CASCADE;
                       """)

    env.cr.execute("""
                       DROP TRIGGER IF EXISTS add_to_order_line_trigger ON sale_order_line;
                   """)
    env.cr.execute("""
                       DROP FUNCTION IF EXISTS trigger_add_to_order_line_function() CASCADE;
                   """)

    env.cr.execute("""
                               DROP TRIGGER IF EXISTS update_to_digitile_pos_order_line_trigger ON sale_order_line;
                           """)
    env.cr.execute("""
                               DROP FUNCTION IF EXISTS trigger_Update_to_order_line_function() CASCADE;
                           """)

    env.cr.execute("""
                                       DROP TRIGGER IF EXISTS update_to_sale_order_line_trigger ON digitile_order_kitchen_line;
                                   """)
    env.cr.execute("""
                                       DROP FUNCTION IF EXISTS trigger_Update_to_sale_order_line_function() CASCADE;
                                   """)

    env.cr.execute("""
                                               DROP TRIGGER IF EXISTS delete_order_line_trigger ON sale_order_line;
                                           """)
    env.cr.execute("""
                                               DROP FUNCTION IF EXISTS trigger_Delete_order_line_function() CASCADE;
                                           """)