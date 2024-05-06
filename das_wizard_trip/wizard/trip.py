from odoo import _, api, fields, models, tools, Command
from odoo.addons.das_publicfunction.controller.main import ProductInfo
import logging
_logger = logging.getLogger(__name__)


class TripWizard(models.TransientModel):
    _name = "trip.wizard"

    driver_id = fields.Many2one('res.partner', string="Driver", required=True, domain=[('is_driver', '=', True)]
                               )
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)


    def action_confirm(self):

        company_id = self.env['res.users'].browse(self.env.uid).company_id.id
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            values = {
                "driver_id": self.driver_id.id,
                "vehicle_id": self.vehicle_id.id,
                # "invoice_ids": active_ids

            }

            trip = self.env['orders.trip'].create(values)
            destinations = []
            for invoice_id in active_ids:
                inv = self.env['account.move'].browse(invoice_id)
                partner_geo = inv.partner_shipping_id
                value = {
                    "lat": partner_geo.partner_latitude,
                    "lng": partner_geo.partner_longitude,
                    "inv_id": invoice_id
                }
                destinations.append(value)
            details = ProductInfo()
            new_destinations = details.sort_points(company_id, destinations)
            _index =0
            for newdes in new_destinations:
                _index = _index + 1
                zone_id =- 1
                inv = self.env['account.move'].browse(newdes[0]['inv_id'])
                # zone_id = details.zone_of_point(inv.partner_shipping_id.partner_latitude,inv.partner_shipping_id.partner_longitude)
                # print('-------partner_latitude-----------',inv.partner_shipping_id.partner_latitude)
                # print('-------partner_longitude-----------',inv.partner_shipping_id.partner_longitude)
                # print('-------zone_id-----------',zone_id)
                # if zone_id != -1:
                #     values = {
                #         'sorting_inv': _index,
                #         'zone_id': zone_id
                #     }
                # else:
                #     values = {
                #         'sorting_inv': _index
                #     }

                values = {
                        'sorting_inv': _index
                    }

                inv.write(values)
                self.env.cr.execute('Insert Into account_move_orders_trip_rel (orders_trip_id,account_move_id) values (' + str(trip.id) + ',' + str(newdes[0]['inv_id']) + ')')
        for rec in self:
            return {
                'name': _('Trip'),
                'view_mode': 'form',
                'view_id': rec.env.ref('orders_trip.order_trip_view_form').id,
                'res_model': 'orders.trip',
                'res_id': trip.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current'}

        # 'res_id': rec.sale_id.id,
        # 'target': 'current',