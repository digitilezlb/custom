from odoo import api, fields, models, _


class ZoneRoute(models.Model):
    _name = 'zone.zone.route'
    _description = 'Zone Route'
    # _order = 'sequence, id'

    zone_id = fields.Many2one('zone.zone', string="Zone")
    street_ids = fields.Many2many('city.street', string="Streets")
    name = fields.Char(string="Name", required=True)
    tracking_iframe = fields.Html("Tracking Preview", sanitize=False, compute='get_route')
    driver_id = fields.Many2one('res.partner', string="Driver", domain="[('is_driver', '=', True)]", required=True)

    @api.onchange('name')
    def streets_domain(self):
        for rec in self:
            all_streets = []
            for line in rec.zone_id.zones_lines:
                for street in line.streets:
                    all_streets.append(street._origin.id)
        return {'domain': {'street_ids': [('id', 'in', all_streets)]}}

    def get_route(self):
        for record in self:
            i = 0
            config = self.env['ir.config_parameter'].sudo()
            get_setting = config.get_param('web_google_maps.google_maps_view_api_key')
            api = get_setting
            if record.street_ids:
                wayPoints = ""
                length = len(record.street_ids)
                for rec in record.street_ids:
                    i += 1
                    if i == 1:
                        origin = str(rec.location_latitude) + "," + str(
                            rec.location_longitude)
                    wayPoints += str(rec.location_latitude) + "," + str(rec.location_longitude)
                    if i != length:
                        wayPoints += "|"
                    else:
                        destination = str(rec.location_latitude) + "," + str(rec.location_longitude)

                src = "https://www.google.com/maps/embed/v1/directions?origin=" + origin + "&amp;waypoints=" + wayPoints + "&amp;destination=" + destination + "&amp;key=" + str(
                    api)

                record.tracking_iframe = f'<iframe width = "600" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'
            else:
                src = "https://www.google.com/maps/embed/v1/directions?origin=34.4371428,35.8286736&amp;destination=34.4523566,35.8140599&amp;key=" + str(
                    api)
                record.tracking_iframe = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src =' + src + ' allowfullscreen = "" />'
