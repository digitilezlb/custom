from odoo import api, fields, models, _


class zone(models.Model):
    _name = 'zone.zone'
    _description = 'Zone'

    name = fields.Char(string="Name", required=True )
    zones_lines = fields.One2many('zone.lines', 'zone_id', string="Zone Lines")
    # marker_color = fields.Char(
    #     string='Marker Color', default='red', required=True)
    marker_color = fields.Selection(
        selection=[
            ('red', 'Red'),
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('black', 'Black'),
            ('white', 'White'),
            ('white', 'White'),
            ('coral', 'Coral'),
            ('orange', 'Orange'),
            ('aqua', 'Aqua'),
            ('blue', 'Blue'),
            ('brown', 'Brown'),
            ('beige', 'Beige'),
        ],
        string="Zone Color",
        default='red',
    )
    geo_id = fields.One2many('latitude.longitude', 'zone_id', string="Geolocation")
    # html_page = fields.Html("Map", sanitize=False, compute='map_page')
    # geo = fields.Text()
    get_map = fields.Html('Drawing', compute="DrawRoute", sanitize=False, store=True)
    # surveyors = fields.One2many('res.partner', 'zone_id', string='Surveyors')
    get_geo_lines = fields.Text('Get the Lines')
    get_drawing = fields.Html(compute="get_drawing_map", sanitize=False, store=True)
    # get_surveyors = fields.Many2many('res.partner', 'zone_surveyor_rel', 'zone_id', 'surveyor_id', string='Surveyor',
    #                              compute="get_surveyors_id", store=True)
    get_retailer = fields.Many2many('res.partner', 'zone_retailer_rel', 'zones_id', 'retailer_ids', string='Retailer',
                                    compute="get_retailer_id", store=True)
    route_id = fields.One2many('zone.zone.route', 'zone_id', string='Route')
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    company_id = fields.Many2one('res.company', string="company", required=True,default= lambda self: self._get_default_value(),)
    get_drivers = fields.Many2many('res.partner', 'zone_driver_rel', 'zones_id', 'driver_ids', string='Drivers',
                                   compute="get_drivers_id", store=True)





    def _get_default_value(self):

        company_id = self.env.company.id

        return company_id


    # @api.depends('surveyors')
    # def get_drivers_id(self):
    #     for rec in self:
    #         if rec.surveyors:
    #             rec.get_drivers = False
    #             for line in rec.surveyors:
    #                 if line.is_driver == True:
    #                     rec.get_drivers = [(4, line.id)]

    # @api.depends('surveyors')
    # def get_surveyors_id(self):
    #     for rec in self:
    #         if rec.surveyors:
    #             rec.get_surveyors = False
    #             for line in rec.surveyors:
    #                 if line.is_surveyor == True:
    #                     rec.get_surveyors = [(4, line.id)]
    #
    # @api.depends('surveyors')
    # def get_retailer_id(self):
    #     for rec in self:
    #         if rec.surveyors:
    #             rec.get_retailer = False
    #             for line in rec.surveyors:
    #                 if line.is_client == True:
    #                     rec.get_retailer = [(4, line.id)]

    def create_draw_map(self):
        for rec in self:
            return {
                'name': _('Draw Map'),
                'view_mode': 'form',
                'view_id': rec.env.ref('das_zone_location.zone_draw_map_view_form').id,
                'res_model': 'zone.draw.map',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new'}

    @api.depends('name')
    def get_drawing_map(self):

        self.get_drawing = f'<iframe width = "100%" height = "650" frameborder = "0"  style = "border:0" src ="/das_zone_location/static/html/map.html?' + str(
            self.id) + '"/>'

    def create_geo_lines(self):
        for rec in self:
            rec.remove_geolocation()
            if rec.get_geo_lines:
                s = rec.get_geo_lines.split('/')
                for line in s:
                    s2 = line.split(',')
                    values = {
                        'latitude': s2[1],
                        'longitude': s2[0],
                        'zone_id': self.id
                    }
                    rec.env['latitude.longitude'].sudo().create(values)
                rec.get_drawing_map()

    def remove_geolocation(self):
        for rec in self:
            # rec.get_geo_lines = ""
            for line in rec.geo_id:
                line.unlink()

    @api.depends('name')
    def DrawRoute(self):
        self.get_map = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src ="/das_zone_location/static/html/draw.html?' + str(
            self.id) + '"/>'


class ZoneLines(models.Model):
    _name = 'zone.lines'
    _description = 'Zone Lines'

    zone_id = fields.Many2one('zone.zone', string="Zone")

    def get_lebanon_states(self):
        lebanon = self.env['res.country'].search([('name', '=', 'Lebanon')])
        lebanon_states = self.env['res.country.state'].search([('country_id', '=', lebanon.id)])
        b = [('id', 'in', lebanon_states.ids)]
        return b

    state = fields.Many2one('res.country.state', string="State", domain=get_lebanon_states)
    city = fields.Many2one('state.city', string="City", domain="[('state_id', '=?', state)]")
    street = fields.Many2one('city.street', string="Street", domain="[('city_id', '=?', city)]")
    streets = fields.Many2many('city.street', string="Streets", domain="[('city_id', '=?', city)]")


class CountryState(models.Model):
    _inherit = 'res.country.state'

    city_ids = fields.One2many('state.city', 'state_id', string="City")
    location_longitude = fields.Float(string="Longitude", digits=(16, 4))
    location_latitude = fields.Float(string="Latitude", digits=(16, 4))


class StateCity(models.Model):
    _name = 'state.city'
    _description = 'State City'

    name = fields.Char(string="Name")
    street_ids = fields.One2many('city.street', 'city_id', string="Streets")
    state_id = fields.Many2one('res.country.state', string="State")
    location_longitude = fields.Float(string="Longitude", digits=(16, 4))
    location_latitude = fields.Float(string="Latitude", digits=(16, 4))


class CityStreet(models.Model):
    _name = 'city.street'
    _description = 'City Streets'
    _order = 'sequence, id'

    name = fields.Char(string="Name")
    name_ar = fields.Char(string="Arabic Name")
    city_id = fields.Many2one('state.city', string="City")
    state = fields.Many2one('res.country.state', string="State", related="city_id.state_id")
    location_longitude = fields.Float(string="Longitude", digits=(16, 4))
    location_latitude = fields.Float(string="Latitude", digits=(16, 4))
    sequence = fields.Integer(string="Sequence", index=True, store=True)


class LatitudeLongitude(models.Model):
    _name = 'latitude.longitude'
    _description = 'Latitude and Longitude'

    latitude = fields.Float(string="Latitude", digits=(16, 4))
    longitude = fields.Float(string="Longitude", digits=(16, 4))
    zone_id = fields.Many2one('zone.zone', string="Zone")
