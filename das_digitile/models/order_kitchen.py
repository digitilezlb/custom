from odoo import fields, models, api


class OrderKitchen(models.Model):
    _name = 'digitile.order.kitchen'
    _description = 'digitile.order.kitchen'

    name = fields.Char(string='name')
    state = fields.Char(string='state')
    date_order = fields.Datetime(string='date_order')
    create_uid = fields.Integer(string='create_uid')
    write_uid = fields.Integer(string='write_uid')
    model_type = fields.Char(string='Origin of Order')
    model_id = fields.Integer(string='model id')
    order_status = fields.Selection(string="Order Status",
                                    selection=[("2", "Draft"),
                                               ("3", "Confirmed"),
                                               ("4", "In Progress"),
                                               ("5", "Ready"),
                                               ("6", "Out For Delivery"),
                                               ("7", "Delivered")
                                               ], default="2", help='To know the status of order', store=True)



    company_id = fields.Many2one('res.company', string="company", required=False)
    sale_order_type = fields.Selection(string="Order Type",
                                       selection=[("1", "Delivery"),
                                                  ("2", "Pick Up"),
                                                  ("3", "Event"),
                                                  ], default="1", help='To know the type of order', store=True,
                                       readonly=False)

    @api.model
    def create_trigger(self):
        # print('call ------------_post_init_hook---------------------------')
        try:
            self.env.cr.execute("""
                                CREATE OR REPLACE FUNCTION trigger_add_to_digitile_order_function()
                                RETURNS TRIGGER AS $$
                                BEGIN
                                    INSERT INTO digitile_order_kitchen  (name,state,date_order,create_uid,write_uid,model_type,model_id,create_date,write_date)
                                    VALUES (NEW.name,NEW.state,NEW.date_order,NEW.create_uid,NEW.write_uid,'sale',NEW.id,
                                    NEW.create_date,NEW.write_date);
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
                                            IF (OLD.name IS DISTINCT FROM NEW.name)  OR (OLD.state IS DISTINCT FROM NEW.state)  OR (OLD.date_order IS DISTINCT FROM NEW.date_order) OR (OLD.amount_total IS DISTINCT FROM NEW.amount_total) THEN
                                                Update digitile_order_kitchen set name=NEW.name,state=NEW.state,date_order=NEW.date_order,create_uid=NEW.create_uid,
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
