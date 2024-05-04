from odoo import api, fields, models, _



class ZoneMap(models.Model):
    _name = 'zone.zone.map'
    _description = 'Zone Map Overview'

    map = fields.Html(compute="get_all_zones", sanitize=False)
    name = fields.Char()

    def get_all_zones(self):
        self.map = f'<iframe width = "100%" height = "500" frameborder = "0"  style = "border:0" src ="/das_zone_location/static/html/all_zones_map.html"/>'

