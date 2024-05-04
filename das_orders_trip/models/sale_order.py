from odoo import fields, models, api, _, exceptions
from datetime import datetime
from odoo.addons.das_publicfunction.controller.main import ProductInfo
from odoo.addons.das_user_notification.controller.main import Notification
import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"
    sorting_inv = fields.Integer()

    # def get_driver_domain(self):
    #     driver_ids = []
    #     excluded_drivers = self.env['orders.trip'].search([('state','=','send')])
    #     excluded =[]
    #     for exl in excluded_drivers:
    #         excluded.append(exl.driver_id.id)

    #     if len(excluded) > 0:
    #         drivers = self.env['res.partner'].sudo().search([('is_driver', '=', True), ('id', 'not in', excluded)])
    #     else:
    #         drivers = self.env['res.partner'].sudo().search([('is_driver', '=', True)])

    #     if drivers:
    #         for driver in drivers:
    #             driver_ids.append(driver.id)

    #     else:
    #         driver_ids.append(-1)

    #     return [('id', 'in', driver_ids)]

    # driver_id = fields.Many2one('res.partner', string="Driver", domain= get_driver_domain)
    # driver_id = fields.Many2one('res.partner', string="Driver",domain= "[('is_driver','=',True)]")
    driver_id = fields.Many2one('res.partner', string="Driver", domain=lambda self: self._get_domain_for_custom_field())
    order_time_to_be_ready = fields.Selection(string="Order Time To Be Ready",
                                              selection=[("0", ""),
                                                         ("10", "10 mins"),
                                                         ("20", "20 mins"),
                                                         ("30", "30 mins"),
                                                         ("40", "40 mins"),
                                                         ("50", "50 mins"),
                                                         ("60", "60 mins"),
                                                         ("70", "70 mins"),
                                                         ("80", "80 mins"),
                                                         ("90", "90 mins"),
                                                         ("100", "100 mins"),
                                                         ("110", "110 mins"),
                                                         ("120", "120 mins"),
                                                         ], store=True,
                                              readonly=False)

    assign_time_time = fields.Datetime("Driver Assigned Time", compute='_compute_assign_time_time', store=True,
                                       readonly=False,
                                       tracking=True)

    def _get_domain_for_custom_field(self):

        company_id = self.env.company.id
        domain = [('is_driver', '=', True), ('company_id', '=', company_id)]
        return domain

    @api.depends('order_time_to_be_ready')
    def _compute_assign_time_time(self):
        try:
            # now_utc = datetime.now(pytz.UTC)
            # current_time = now_utc.astimezone(ProductInfo.beirut_timezone)
            for rec in self:
                if self.order_time_to_be_ready:

                    rec.assign_time_time = datetime.now()
                else:
                    rec.assign_time_time = None
        except:
            pass

    @api.model
    def create(self, vals):

        sale_order = super(SaleOrder, self).create(vals)
        try:

            # if vals['driver_id']:

            #     trip = self.env['orders.trip'].sudo().search([('driver_id','=',vals['driver_id']),('state','=','draft')],limit=1)
            #     if trip:
            #         trip.order_ids = [(4, sale_order.id)]
            #     else:
            #         vehicle = self.env['fleet.vehicle'].sudo().search([('driver_id','=',vals['driver_id'])],limit=1)
            #         if vehicle== False :
            #             vehicle = self.env['fleet.vehicle'].sudo().search([], limit=1)
            #         trip = self.env['orders.trip'].sudo().create({
            #             "driver_id": vals['driver_id'],
            #             "vehicle_id": vehicle.id,
            #             "order_ids": [(4, sale_order.id)]
            #         })

            if 'order_time_to_be_ready' in vals:
                if 'driver_id' in vals:
                    driver = self.env['res.partner'].sudo().search([('id', '=', vals['driver_id'])], limit=1)

                    driver_user = self.env['res.users'].sudo().search([('partner_id', '=', driver.id)], limit=1)

                    if driver_user:
                        notification = Notification
                        message_name = "اضافة طلبية"

                        message_description = "لقد تم اضافة الطلبية رقم " + sale_order.name + " الى رحلتك" + ". الوقت المتبقي لتجهيز الطلبية هو :" + \
                                              vals['order_time_to_be_ready']
                        chat_id = '1'
                        notification.send_notification(self.env.user, driver_user, message_name, message_description,
                                                       sale_order.id)
        except:
            pass

        return sale_order

    @api.onchange('order_status')
    def on_change_order_status(self):

        # try:
        old_value = int(self._origin.order_status)
        new_value = int(self.order_status)
        if old_value == 6 or old_value == 7:
            if new_value < old_value:
                raise exceptions.UserError("You can't change")

        # except:
        #     pass

    def write(self, vals):

        # try:
        #     old_driver = self.env['sale.order'].sudo().search([('id','=',self._origin.id)])
        #     if old_driver.driver_id:
        #         old_driver_id = old_driver.driver_id
        #     if old_driver.order_time_to_be_ready:
        #         old_order_time_to_be_ready = old_driver.order_time_to_be_ready

        # except:
        #     pass
        sale_order = super(SaleOrder, self).write(vals)

        driver = False
        driver_user = False
        send_notif = False
        if ('order_time_to_be_ready' in vals) or ('driver_id' in vals):

            driver = False
            if 'driver_id' in vals:
                if vals['driver_id']:
                    driver = self.env['res.partner'].sudo().search([('id', '=', vals['driver_id'])], limit=1)
                elif self.driver_id:
                    driver = self.env['res.partner'].sudo().search([('id', '=', self.driver_id.id)], limit=1)
            else:
                if self.driver_id:
                    driver = self.env['res.partner'].sudo().search([('id', '=', self.driver_id.id)], limit=1)
            if driver:
                driver_user = self.env['res.users'].sudo().search([('partner_id', '=', driver.id)], limit=1)
            else:
                driver_user = False
            send_notif = False

            if ('order_time_to_be_ready' in vals):
                if vals['order_time_to_be_ready']:
                    send_notif = True
                    assign_time = vals['order_time_to_be_ready']
                else:
                    send_notif = False
            else:
                if self.order_time_to_be_ready:
                    send_notif = True
                    assign_time = self.order_time_to_be_ready
                else:
                    send_notif = False

            if driver_user and send_notif:
                notification = Notification
                message_name = "اضافة طلبية"
                message_description = "لقد تم اضافة الطلبية رقم " + self.name + " الى رحلتك" + ". الوقت المتبقي لتجهيز الطلبية هو :" + assign_time

                notification.send_notification(self.env.user, driver_user, message_name, message_description,
                                               self._origin.id)
        else:
            if self.driver_id:
                driver = self.env['res.partner'].sudo().search([('id', '=', self.driver_id.id)], limit=1)
            if driver:
                driver_user = self.env['res.users'].sudo().search([('partner_id', '=', driver.id)], limit=1)

            else:
                driver_user = False
            if self.order_time_to_be_ready:
                send_notif = True

            else:
                send_notif = False

        try:
            if driver_user and send_notif:
                if 'order_status' in vals:
                    if vals['order_status'] == '5':
                        notification1 = Notification
                        message_name = "تجهيز طلبية"
                        message_description = "لقد تم تجهيز الطلبية رقم " + self.name
                        chat_id = '1'
                        notification1.send_notification(self.env.user, driver_user, message_name, message_description,
                                                        self._origin.id)

            try:
                if 'order_status' in vals:
                    if vals['order_status'] == '5' or vals['order_status'] == '6' or vals['order_status'] == '7':
                        notification = Notification
                        quotation = self.env['sale.order'].sudo().search([('id', '=', self._origin.id)])
                        if vals['order_status'] == '5':
                            message_name = "تجهيز طلبية"
                            message_description = "لقد تم تجهيز الطلبية رقم " + self.name
                        elif vals['order_status'] == '6':
                            message_name = "طلبية قيد التوصيل"
                            message_description = "الطلبية رقم " + self.name + " أصبحت قيد التوصيل"
                        elif vals['order_status'] == '7':
                            message_name = "توصيل طلبية"
                            message_description = "لقد تم توصيل الطلبية رقم " + self.name
                            try:
                                self.picking_ids.action_set_quantities_to_reservation()
                                self.picking_ids.button_validate()
                            except:
                                pass
                        chat_id = '1'

                        managers = self.env['res.partner'].sudo().search(
                            [('is_manager', '=', 'True'), ('company_id', '=', quotation.company_id.id)])
                        if managers:
                            for manager in managers:
                                manager_user = self.env['res.users'].sudo().search(
                                    [('partner_id', '=', manager.id)])
                                if manager_user:
                                    notification.send_notification(self.env.user, manager_user, message_name,
                                                                   message_description,
                                                                   quotation.id)

            except:
                pass

        except:
            pass
        return sale_order
