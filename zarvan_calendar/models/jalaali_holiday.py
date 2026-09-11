# -*- coding: utf-8 -*-
from odoo import models, fields, api

class JalaaliHoliday(models.Model):
    """Model to store Persian holidays."""
    _name = 'jalaali.holiday'
    _description = 'Jalali Holiday'
    _order = 'month, day'

    name = fields.Char(string="Holiday Name", required=True)
    month = fields.Integer(string="Month (Jalali)", required=True)
    day = fields.Integer(string="Day (Jalali)", required=True)
    type = fields.Selection([
        ('fixed', 'Fixed Date'),
        ('lunar', 'Lunar/Islamic (Calculated)'),
    ], string="Type", default='fixed', required=True)
    
    is_national = fields.Boolean(string="National Holiday", default=True)
    description = fields.Text(string="Description")

    @api.constrains('month', 'day')
    def _check_valid_date(self):
        for record in self:
            if not (1 <= record.month <= 12):
                raise ValidationError("Month must be between 1 and 12")
            if not (1 <= record.day <= 31):
                raise ValidationError("Day must be between 1 and 31")
