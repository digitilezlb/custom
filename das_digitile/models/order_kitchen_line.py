from odoo import fields, models
from odoo import api


class OrderKitchenLine(models.Model):
    _name = 'digitile.order.kitchen.line'
    _description = 'digitile.order.kitchen.line'

    name = fields.Char(string='Name')
    state = fields.Char(string='state')
    create_uid = fields.Integer(string='create_uid')
    write_uid = fields.Integer(string='write_uid')
    product_id = fields.Many2one('product.product')
    qtity = fields.Float(string='Quantity')
    model_type = fields.Char(string='Origin of Order')
    model_id = fields.Integer(string='model id')
    notes = fields.Char(string="Notes")
    order_kitchen_id = fields.Integer(string='order kitchen')
    order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                               ("3", "Confirmed"),    
                                               ("4", "In Progress"),
                                               ("5", "Ready")
                                               ], default="2", help='To know the status of order', store=True)



    @api.model
    def create_trigger(self):
        # print('call ------------_post_init_hook---------------------------')

        # --------------Insert Order_Line
        try:
            self.env.cr.execute("""
                                    CREATE OR REPLACE FUNCTION trigger_add_to_order_line_function()
                                    RETURNS TRIGGER AS $$
                                    BEGIN
                                        INSERT INTO digitile_order_kitchen_line  (name,state,product_id,qtity,create_uid,write_uid,model_type,model_id,notes,create_date,write_date,order_kitchen_id)
                                        VALUES (NEW.name,NEW.state,NEW.product_id,NEW.product_uom_qty ,NEW.create_uid,NEW.write_uid,'sale',NEW.id,NEW.notes,
                                        NEW.create_date,NEW.write_date,(select id from digitile_order_kitchen where model_id=NEW.order_id and model_type='sale' ));
                                        RETURN NEW;
                                    END;
                                    $$ LANGUAGE plpgsql;
                                """)

            self.env.cr.execute("""
                                    CREATE  TRIGGER add_to_order_line_trigger
                                    AFTER INSERT ON sale_order_line
                                    FOR EACH ROW
                                    EXECUTE FUNCTION trigger_add_to_order_line_function();
                                """)

            # --------------Update Order_Line
            self.env.cr.execute("""
                                            CREATE OR REPLACE FUNCTION trigger_Update_to_order_line_function()
                                            RETURNS TRIGGER AS $$
                                            BEGIN
                                                IF (OLD.notes IS DISTINCT FROM NEW.notes) OR (OLD.product_uom_qty IS DISTINCT FROM NEW.product_uom_qty) OR (OLD.name IS DISTINCT FROM NEW.name) OR (OLD.state IS DISTINCT FROM NEW.state)  OR (OLD.product_id IS DISTINCT FROM NEW.product_id) THEN
                                                        Update digitile_order_kitchen_line set notes=New.notes, name=NEW.name,state=NEW.state,product_id=NEW.product_id,
                                                        qtity=NEW.product_uom_qty ,create_uid=NEW.create_uid,
                                                        write_uid=NEW.write_uid  where  model_id = OLD.id And model_type='sale' ;
                                                END IF;
                                                RETURN NEW;
                                            END;
                                            $$ LANGUAGE plpgsql;
                                        """)

            self.env.cr.execute("""
                                            CREATE  TRIGGER update_to_digitile_pos_order_line_trigger
                                            AFTER UPDATE  ON sale_order_line
                                            FOR EACH ROW
                                            EXECUTE FUNCTION trigger_Update_to_order_line_function();
                                        """)

            # --------------Update digitile_order_kitchen_line
            self.env.cr.execute("""
                                                            CREATE OR REPLACE FUNCTION trigger_Update_to_sale_order_line_function()
                                                                RETURNS TRIGGER AS $$
                                                                BEGIN
                                                                    IF OLD.order_status IS DISTINCT FROM NEW.order_status THEN
        																Update sale_order_line set order_status=NEW.order_status where id = OLD.model_id  ;
        															END IF;
                                                                    RETURN NEW;
                                                                END;
                                                                $$ LANGUAGE plpgsql;
                                                        """)

            self.env.cr.execute("""
                                                                        CREATE  TRIGGER update_to_sale_order_line_trigger
                                                                        AFTER UPDATE  ON digitile_order_kitchen_line
                                                                        FOR EACH ROW
                                                                        EXECUTE FUNCTION trigger_Update_to_sale_order_line_function();
                                                                    """)


            # --------------Delete Order_Line

            self.env.cr.execute("""
                                                    CREATE OR REPLACE FUNCTION trigger_Delete_order_line_function()
                                                    RETURNS TRIGGER AS $$
                                                    BEGIN
                                                         delete from digitile_order_kitchen_line  where  model_id = OLD.id And model_type='sale' ;
                                                        RETURN NEW;
                                                    END;
                                                    $$ LANGUAGE plpgsql;
                                                """)

            self.env.cr.execute("""
                                                    CREATE  TRIGGER delete_order_line_trigger
                                                    AFTER DELETE  ON sale_order_line
                                                    FOR EACH ROW
                                                    EXECUTE FUNCTION trigger_Delete_order_line_function();
                                                """)
        except:
            pass
