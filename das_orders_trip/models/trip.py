from odoo import fields, models, api, _
from datetime import datetime, timedelta
import json
import requests
from odoo.exceptions import UserError, ValidationError


class OrdersTrip(models.Model):
    _name = "orders.trip"
    _description = "Trip of orders"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Shipment Reference", required=True, copy=False, index=True, readonly=True,
                       default=lambda self: _('New'), track_visibility='always')
    reference = fields.Char(string="Reference", store=True, readonly=True, track_visibility='always')
    driver_id = fields.Many2one('res.partner', string="Driver", required=True,domain=[('is_driver', '=', True)],
                                track_visibility='always')

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True, track_visibility='always')
    delivered_date = fields.Datetime(string='delivered date')

    # invoice_ids = fields.Many2many('account.move', string='Invoices',order='sorting_inv Asc')

    order_ids = fields.Many2many('sale.order', string='Orders',order='sorting_inv Asc')

    state = fields.Selection([('draft', 'Draft'), ('send', 'Send'), ('arrived', 'Arrived')], default='draft')
    tracking_iframe = fields.Html("Tracking Preview", sanitize=False, compute='get_route', track_visibility='always')

    total = fields.Float(string='Total')
    delivered_total = fields.Float(string='Collected')
    rest_total = fields.Float(string='Rest')


    @api.depends("driver_id")
    def get_sale_order_domain(self):
        sale_order_ids = []
        if self.driver_id:
            sales = self.env['sale.order'].sudo().search(
                [('driver_id', '=', self.driver_id.id),('order_status','in',['2','3','4','5'])])

            trip_id = self.id
            value = str(trip_id)
            if self._origin.id:
                trip_id = self._origin.id

            else:
                trip_id = -1

            for sale in sales:
                query = 'Select * From orders_trip_sale_order_rel where sale_order_id=' + str(sale.id)
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                if res:
                    if len(res) == 0:
                        sale_order_ids.append(sale.id)
                else:
                    sale_order_ids.append(sale.id)

        self.sale_list = [(6, 0, sale_order_ids)]

    sale_list = fields.Many2many('sale.order', 'your_sale_related_model', store=True, compute=get_sale_order_domain)


    @api.onchange('driver_id')
    def get_orders(self):
        sale_order_ids = []
        if self.driver_id:
            sales = self.env['sale.order'].sudo().search(
                [('driver_id', '=', self.driver_id.id), ('order_status', 'in', ['2', '3', '4', '5'])])

            trip_id = self.id
            value = str(trip_id)
            if self._origin.id:
                trip_id = self._origin.id

            else:
                trip_id = -1


            for sale in sales:

                query = 'Select * From orders_trip_sale_order_rel where sale_order_id=' + str(sale.id) + ' And orders_trip_id <>' + str(trip_id)
                self.env.cr.execute(query)
                res = self.env.cr.fetchall()
                if res:
                    if len(res) == 0:
                        sale_order_ids.append(sale.id)
                else:
                    sale_order_ids.append(sale.id)

            sale_order_s = self.env['sale.order'].browse(sale_order_ids)  # 'self' refers to the current recordset

            self.order_ids = sale_order_s


    def get_route(self):
        for record in self:
            i = 0
            total = 0
            delivered_total = 0
            rest_total = 0

            if record.order_ids:

                company_id = self.env['res.users'].browse(self.env.uid).company_id.id
                company = self.env['res.company'].sudo().search([('id', '=', company_id)])
                wayPoints = ""
                length = len(record.order_ids)
                source = str(company.partner_id.partner_latitude) + "," + str(
                    company.partner_id.partner_longitude)

                orders = []
                # _index = 0
                for rec in record.order_ids:

                    total = total + rec.amount_total
                    if rec.order_status=='7':
                        delivered_total = delivered_total + rec.amount_total

                    orders.append((rec.id,rec.sorting_inv,rec.partner_shipping_id.partner_latitude,rec.partner_shipping_id.partner_longitude))

                sorted_orders = sorted(orders, key=lambda x: x[1])

                for inv_id in sorted_orders:
                    i += 1
                    wayPoints += str(inv_id[2]) + "," + str(
                        inv_id[3])

                    if i != length:
                        wayPoints += "|"
                    elif i == length:
                        destination = str(inv_id[2]) + "," + str(
                            inv_id[3])
                src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyAszKHeYYSkYMtOvKezIgF5--u7gLkfSog&amp;origin=" + source + "&amp;destination=" + destination + "&amp;waypoints=" + wayPoints + "&amp;language=en"

                record.tracking_iframe = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'
                rest_total = total - delivered_total
                self.total = total
                self.delivered_total = delivered_total
                self.rest_total = rest_total

            else:
                src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyAszKHeYYSkYMtOvKezIgF5--u7gLkfSog&amp;origin=33.8937744,35.5508923&amp;destination=33.8937744,35.5508923&amp;language=en"
                record.tracking_iframe = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'

    def get_new_route(self):
        for record in self:
            i = 0
            total = 0
            delivered_total = 0
            rest_total = 0
            if record.order_ids:
                company_id = self.env['res.users'].browse(self.env.uid).company_id.id
                company = self.env['res.company'].sudo().search([('id', '=', company_id)])
                wayPoints = ""
                length = len(record.order_ids)
                source = str(company.partner_id.partner_latitude) + "," + str(
                    company.partner_id.partner_longitude)

                orders = []
                _index = 0
                for rec in record.order_ids:

                    total = total + rec.amount_total
                    if rec.order_status=='7':
                        delivered_total = delivered_total + rec.amount_total

                    _index = _index + 1
                    orders.append((rec.id,rec.sorting_inv,rec.partner_shipping_id.partner_latitude,rec.partner_shipping_id.partner_longitude))

                sorted_orders = sorted(orders, key=lambda x: x[1])

                for inv_id in sorted_orders:
                    i += 1
                    wayPoints += str(inv_id[2]) + "," + str(
                        inv_id[3])

                    if i != length:
                        wayPoints += "|"
                    elif i == length:
                        destination = str(inv_id[2]) + "," + str(
                            inv_id[3])
                src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyAszKHeYYSkYMtOvKezIgF5--u7gLkfSog&amp;origin=" + source + "&amp;destination=" + destination + "&amp;waypoints=" + wayPoints + "&amp;language=en"

                record.tracking_iframe = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'

                rest_total = total - delivered_total
                self.total = total
                self.delivered_total = delivered_total
                self.rest_total = rest_total
            else:
                src = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyAszKHeYYSkYMtOvKezIgF5--u7gLkfSog&amp;origin=33.8937744,35.5508923&amp;destination=33.8937744,35.5508923&amp;language=en"
                record.tracking_iframe = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'


    def send_trip(self):
        self.state = 'send'

        for record in self:
            i = 0
            total = 0
            delivered_total = 0
            rest_total = 0
            if record.order_ids:
                for rec in record.order_ids:
                    rec.write({'order_status':"6"})


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('trip.reference') or _('New')
        result = super(OrdersTrip, self).create(vals)
        result.get_reference()
        return result

    def get_reference(self):
        for rec in self:
            _date = datetime.now()
            rec.reference = "TR-" + str(_date.strftime("%y")) + '' + str(
                _date.strftime("%m")) + '' + str(
                _date.strftime("%d")) + '-' + rec.name

