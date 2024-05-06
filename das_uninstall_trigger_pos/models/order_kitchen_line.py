from odoo import fields, models
from odoo import api


class OrderKitchenLine(models.Model):
    _inherit = 'digitile.order.kitchen.line'




    @api.model
    def create_trigger_pos(self):
        try:
            self.env.cr.execute("""
                                    CREATE OR REPLACE FUNCTION trigger_add_pos_to_order_line_function()
                                    RETURNS TRIGGER AS $$
                                    BEGIN
                                        INSERT INTO digitile_order_kitchen_line  (name,order_status,product_id,qtity,create_uid,write_uid,model_type,model_id,create_date,write_date,order_kitchen_id)
                                        VALUES (NEW.name,'4',NEW.product_id,NEW.qty ,NEW.create_uid,NEW.write_uid,'pos',NEW.id,
                                        NEW.create_date,NEW.write_date,(select id from digitile_order_kitchen where model_id=NEW.order_id and model_type='pos' ));
                                        RETURN NEW;
                                    END;
                                    $$ LANGUAGE plpgsql;
                                """)

            self.env.cr.execute("""
                                    CREATE  TRIGGER add_pos_to_order_line_trigger
                                    AFTER INSERT ON pos_order_line
                                    FOR EACH ROW
                                    EXECUTE FUNCTION trigger_add_pos_to_order_line_function();
                                """)

            # --------------Update Order_Line
            self.env.cr.execute("""
                                            CREATE OR REPLACE FUNCTION trigger_Update_pos_to_order_line_function()
                                            RETURNS TRIGGER AS $$
                                            BEGIN
                                                IF (OLD.qty IS DISTINCT FROM NEW.qty) OR (OLD.name IS DISTINCT FROM NEW.name)    OR (OLD.order_status IS DISTINCT FROM NEW.order_status)   OR (OLD.product_id IS DISTINCT FROM NEW.product_id) THEN
                                                        Update digitile_order_kitchen_line set  name=NEW.name,order_status=NEW.order_status,  product_id=NEW.product_id,
                                                        qtity=NEW.qty ,create_uid=NEW.create_uid,
                                                        write_uid=NEW.write_uid  where  model_id = OLD.id And model_type='pos' ;
                                                END IF;
                                                RETURN NEW;
                                            END;
                                            $$ LANGUAGE plpgsql;
                                        """)

            self.env.cr.execute("""
                                            CREATE  TRIGGER update_pos_to_digitile_pos_order_line_trigger
                                            AFTER UPDATE  ON pos_order_line
                                            FOR EACH ROW
                                            EXECUTE FUNCTION trigger_Update_pos_to_order_line_function();
                                        """)

            # --------------Update digitile_order_kitchen_line
            self.env.cr.execute("""
                                                            CREATE OR REPLACE FUNCTION trigger_Update_pos_to_pos_order_line_function()
                                                                RETURNS TRIGGER AS $$
                                                                BEGIN
                                                                    IF OLD.order_status IS DISTINCT FROM NEW.order_status THEN
        																Update pos_order_line set order_status=NEW.order_status where id = OLD.model_id  ;
        															END IF;
                                                                    RETURN NEW;
                                                                END;
                                                                $$ LANGUAGE plpgsql;
                                                        """)

            self.env.cr.execute("""
                                                                        CREATE  TRIGGER update_to_pos_order_line_trigger
                                                                        AFTER UPDATE  ON digitile_order_kitchen_line
                                                                        FOR EACH ROW
                                                                        EXECUTE FUNCTION trigger_Update_pos_to_pos_order_line_function();
                                                                    """)

            # --------------Delete Order_Line

            self.env.cr.execute("""
                                                    CREATE OR REPLACE FUNCTION trigger_Delete_pos_order_line_function()
                                                    RETURNS TRIGGER AS $$
                                                    BEGIN
                                                         delete from digitile_order_kitchen_line  where  model_id = OLD.id And model_type='pos' ;
                                                        RETURN NEW;
                                                    END;
                                                    $$ LANGUAGE plpgsql;
                                                """)

            self.env.cr.execute("""
                                                    CREATE  TRIGGER delete_pos_order_line_trigger
                                                    AFTER DELETE  ON pos_order_line
                                                    FOR EACH ROW
                                                    EXECUTE FUNCTION trigger_Delete_pos_order_line_function();
                                                """)
        except:
            pass

