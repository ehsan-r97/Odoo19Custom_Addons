# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import jdatetime


class JalaaliMixin(models.AbstractModel):
    """
    Mixin to add Jalali date validation and conversion to any model.
    
    Usage:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['jalaali.mixin']
            
            my_date = fields.Date()
    """
    _name = 'jalaali.mixin'
    _description = 'Jalali Calendar Mixin'

    def _jalali_to_gregorian(self, jalali_date_str):
        """
        Convert Jalali date string (YYYY-MM-DD) to Gregorian date object.
        
        Args:
            jalali_date_str: String in format '1403-01-15' or '1403/01/15'
            
        Returns:
            datetime.date object or None if invalid
        """
        try:
            # Normalize separators
            normalized = jalali_date_str.replace('/', '-')
            parts = normalized.split('-')
            if len(parts) != 3:
                return None
            
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Validate ranges
            if not (1300 <= year <= 1500):
                return None
            if not (1 <= month <= 12):
                return None
            if not (1 <= day <= 31):
                return None
            
            # Convert using jdatetime
            j_date = jdatetime.date(year, month, day)
            g_date = j_date.togregorian()
            return g_date
        except (ValueError, AttributeError):
            return None

    def _gregorian_to_jalali(self, gregorian_date):
        """
        Convert Gregorian date to Jalali string (YYYY-MM-DD).
        
        Args:
            gregorian_date: datetime.date or datetime.datetime object
            
        Returns:
            String in format '1403-01-15' or None if invalid
        """
        try:
            if isinstance(gregorian_date, datetime):
                gregorian_date = gregorian_date.date()
            
            j_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return j_date.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            return None

    def _validate_jalali_date(self, jalali_date_str, field_name='Date'):
        """
        Validate a Jalali date string.
        
        Args:
            jalali_date_str: Date string to validate
            field_name: Name of the field for error messages
            
        Raises:
            ValidationError: If date is invalid
        """
        if not jalali_date_str:
            return True
            
        g_date = self._jalali_to_gregorian(jalali_date_str)
        if g_date is None:
            raise ValidationError(_(
                "Invalid Jalali date for %(field)s: %(date)s\n"
                "Expected format: YYYY-MM-DD (e.g., 1403-01-15)"
            ) % {'field': field_name, 'date': jalali_date_str})
        
        # Check for leap year validity
        try:
            j_date = jdatetime.date.fromgregorian(date=g_date)
            # If conversion back fails, it's an invalid Jalali date
            j_date.togregorian()
        except ValueError:
            raise ValidationError(_(
                "Invalid Jalali date: %(date)s is not a valid date (check leap year)"
            ) % {'date': jalali_date_str})
        
        return True

    @api.constrains('date')  # Override this in your model
    def _check_jalali_dates(self):
        """Override this method in your model to validate specific fields."""
        pass


class ResUsers(models.Model):
    """Add Jalali preferences to users."""
    _inherit = 'res.users'

    use_jalali_calendar = fields.Boolean(
        string="Use Jalali Calendar",
        default=False,
        help="Display dates in Jalali format in forms and reports"
    )
    
    jalali_show_holidays = fields.Boolean(
        string="Show Holidays in Calendar",
        default=True,
        help="Display Persian holidays in calendar views"
    )
    
    jalali_week_start = fields.Selection([
        ('6', 'Saturday'),
        ('0', 'Monday'),
    ], string="Week Start Day", default='6',
       help="First day of the week for Jalali calendar")
