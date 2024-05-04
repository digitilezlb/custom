from odoo import api, fields, models, _
from datetime import datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta



class ContactEdits(models.Model):
    _inherit = 'res.partner'
    _description = 'inherit Contacts'

    km_home_work = fields.Integer(string="Home-Work Distance")
    identification_id = fields.Char(string='Identification No')
    passport_id = fields.Char(string='Passport No')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    birthday = fields.Date('Date of Birth')
    country_of_birth = fields.Many2one('res.country', string="Country of Birth")
    place_of_birth = fields.Char(string='Place of Birth')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single')
    spouse_complete_name = fields.Char(string="Spouse Complete Name")
    spouse_birthdate = fields.Date(string="Spouse Birthdate")
    children = fields.Integer(string='Number of Children')
    certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other')
    study_field = fields.Char(string="Field of Study")
    study_school = fields.Char(string="School")
    budget = fields.Float(string='Budget')
    is_driver = fields.Boolean(string='Is Driver', default=False)
    is_hidden = fields.Boolean()
    
    @api.model
    def create(self, vals):
        result = super(ContactEdits, self).create(vals)
        if result.is_driver == True:
            self.env['hr.employee'].sudo().create({'name': result.name
              
            })
        return result

    # def set_driver(self):
    #     for rec in self:
    #         rec.is_driver = True
    #
    # def unset_driver(self):
    #     for rec in self:
    #         rec.is_driver = False

    @api.constrains('birthday')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.birthday and rec.birthday > fields.Date.today():
                raise ValidationError(_("The entered date of birthday is not acceptable !"))

    @api.constrains('spouse_birthdate')
    def _check_birth(self):
        for rec in self:
            if rec.spouse_birthdate and rec.spouse_birthdate > fields.Date.today():
                raise ValidationError(_("The entered date of birthday is not acceptable !"))



class TypeDriver(models.Model):
    _inherit = 'fleet.vehicle'
    _description = 'inherit freelance'

    type_driver = fields.Selection([
        ('freelance', 'Freelance'),
        ('employee', 'Employee'),
    ],string="Driver Type")
    # volume = fields.Float(string='Volume')
    weight = fields.Float(string='Weight')
