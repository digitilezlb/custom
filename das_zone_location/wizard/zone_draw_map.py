from odoo import api, fields, models


class ZoneMapDraw(models.TransientModel):
    _name = 'zone.draw.map'
    _description = 'Zone Draw Map'

    get_map = fields.Html('Drawing', compute="DrawRoute", sanitize=False, store=True)
    zone_id = fields.Many2one('zone.zone', string="Zone")

    @api.depends('zone_id')
    def DrawRoute(self):
        self.get_map = f'<iframe width = "100%" height = "450" frameborder = "0"  style = "border:0" src ="/das_zone_location/static/html/draw.html?' + str(
            self.zone_id.id) + '"/>'
