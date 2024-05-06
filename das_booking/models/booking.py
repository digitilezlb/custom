from odoo import api, fields, models, exceptions

class AboutUs(models.Model):
    _name = "booking.booking"
    _description = "booking.booking"

    name = fields.Char(string='Full Name',required=True )
    nb_people = fields.Integer(string='Number of People',default=1,required=True )
    the_date = fields.Date(string='Date',required=True)
    the_time = fields.Datetime(string='Time',required=True)
    comments = fields.Text(string='Comments')
    company_id = fields.Many2one('res.company', string="company", required=False)
    delivery_time = fields.Float(string='Time', compute='_compute_delivery_time', store=True)

    @api.depends('the_time')
    def _compute_delivery_time(self):
        for record in self:
            if record.the_time:
                record.delivery_time = record.the_time.hour + record.the_time.minute / 60.0
            else:
                record.delivery_time = 0.0

