from odoo import fields, models, api


class OrderKitchen(models.Model):
    _inherit = 'digitile.order.kitchen'

    delivery_date = fields.Datetime(
        string="Delivery Date",
        required=False,
        help="Creation date of delivery orders.")

    @api.model
    def create_trigger(self):

        try:
            self.env.cr.execute("""
                                CREATE OR REPLACE FUNCTION trigger_add_to_digitile_order_function()
                                RETURNS TRIGGER AS $$
                                BEGIN
                                    INSERT INTO digitile_order_kitchen  (name,company_id,sale_order_type,state,order_status,date_order,create_uid,write_uid,model_type,model_id,create_date,write_date,delivery_date)
                                    VALUES (NEW.name,NEW.company_id,NEW.sale_order_type,NEW.state,NEW.order_status,NEW.date_order,NEW.create_uid,NEW.write_uid,'sale',NEW.id,
                                    NEW.create_date,NEW.write_date,NEW.delivery_date);
                                    RETURN NEW;
                                END;
                                $$ LANGUAGE plpgsql;
                            """)

            self.env.cr.execute("""
                                CREATE  TRIGGER add_to_digitile_order_trigger
                                AFTER INSERT ON sale_order
                                FOR EACH ROW
                                EXECUTE FUNCTION trigger_add_to_digitile_order_function();
                            """)

            self.env.cr.execute("""
                                        CREATE OR REPLACE FUNCTION trigger_Update_to_digitile_order_function()
                                        RETURNS TRIGGER AS $$
                                        BEGIN
                                            IF (OLD.name IS DISTINCT FROM NEW.name) OR (OLD.order_status IS DISTINCT FROM NEW.order_status)  OR (OLD.state IS DISTINCT FROM NEW.state)  OR (OLD.date_order IS DISTINCT FROM NEW.date_order) OR (OLD.amount_total IS DISTINCT FROM NEW.amount_total) THEN
                                                Update digitile_order_kitchen set name=NEW.name,state=NEW.state,company_id=NEW.company_id,sale_order_type=NEW.sale_order_type, order_status=NEW.order_status, date_order=NEW.date_order,create_uid=NEW.create_uid,
                                                write_uid=NEW.write_uid  where  model_id = OLD.id And model_type='sale' ;
                                            END IF;
                                            RETURN NEW;
                                        END;
                                        $$ LANGUAGE plpgsql;
                                    """)

            self.env.cr.execute("""
                                        CREATE  TRIGGER update_to_digitile_order_trigger
                                        AFTER UPDATE ON sale_order
                                        FOR EACH ROW
                                        EXECUTE FUNCTION trigger_Update_to_digitile_order_function();
                                    """)

            self.env.cr.execute("""
                                                            CREATE OR REPLACE FUNCTION trigger_Update_to_sale_order_function()
                                                            RETURNS TRIGGER AS $$
                                                            BEGIN
                                                                IF (OLD.order_status IS DISTINCT FROM NEW.order_status) THEN
                                                                    Update sale_order set order_status=NEW.order_status where id = OLD.model_id  ;
                                                                END IF;
                                                                RETURN NEW;
                                                            END;
                                                            $$ LANGUAGE plpgsql;
                                                        """)

            self.env.cr.execute("""
                                                            CREATE  TRIGGER update_to_sale_order_trigger
                                                            AFTER UPDATE ON digitile_order_kitchen
                                                            FOR EACH ROW
                                                            EXECUTE FUNCTION trigger_Update_to_sale_order_function();
                                                        """)
        except:
            pass
