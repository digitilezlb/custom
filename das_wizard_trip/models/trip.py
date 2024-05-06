from odoo import fields, models, api, _
from odoo.addons.das_publicfunction.controller.main import ProductInfo

class Trip(models.Model):
    _inherit = "account.move"

    zone_id = fields.Many2one('zone.zone', compute='get_zone', store=False)

    invoice_partner_shipping_id_display_name = fields.Char(string="Shipping Address", compute='_compute_invoice_partner_display_info', store=False)

    @api.depends('partner_shipping_id')
    def _compute_invoice_partner_display_info(self):
        for contact in self:
            name = ''

            if contact.partner_shipping_id:
                # thepartner = self.env['res.partner'].search(['id','=',contact.partner_shipping_id.id])
                thepartner = contact.partner_shipping_id
            else:
                # thepartner = self.env['res.partner'].search(['id', '=', contact.partner_id.id])
                thepartner =  contact.partner_id

            if thepartner:
                # if thepartner.parent_id:

                if thepartner.city_id:
                    name = thepartner.city_id.name
                if thepartner.street_id:
                    if name !='':
                        name = name + ', ' + thepartner.street_id.name
                    else:
                        name = thepartner.street_id.name

                if thepartner.street2:
                    if name !='':
                        name = name + ', ' + thepartner.street2
                    else:
                        name = thepartner.street2

                # else:
                #     name = thepartner.name

            else:
                name = contact.name
            contact.invoice_partner_shipping_id_display_name = name

    @api.depends('partner_shipping_id')
    def get_zone(self):
        details = ProductInfo()
        for rec in self:
            rec.zone_id = details.zone_of_point(rec.partner_shipping_id.partner_latitude,
                                        rec.partner_shipping_id.partner_longitude)

    def create_trip(self):
        for rec in self:
            return {
                'name': _('Create Trip'),
                'view_mode': 'form',
                'view_id': rec.env.ref('wizard_trip.trip_wizard').id,
                'res_model': 'trip.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new'}
