# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import re

class JalaaliMixin(models.AbstractModel):
    """
    Mixin to add automatic Jalali/Gregorian conversion to any model.
    
    Usage:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['jalaali.mixin']
            
            meeting_date = fields.Date()
            meeting_time = fields.Datetime()
            
            # Enable auto-conversion for these fields
            _jalaali_date_fields = ['meeting_date']
            _jalaali_datetime_fields = ['meeting_time']
    """
    _name = 'jalaali.mixin'
    _description = 'Jalali Conversion Mixin'
    
    _jalaali_date_fields = []
    _jalaali_datetime_fields = []
    
    @api.model_create_multi
    def create(self, vals_list):
        """Convert Jalali dates to Gregorian before creating records."""
        self._convert_jalali_to_gregorian(vals_list)
        return super().create(vals_list)
    
    def write(self, vals):
        """Convert Jalali dates to Gregorian before writing records."""
        self._convert_jalali_to_gregorian([vals])
        return super().write(vals)
    
    def _convert_jalali_to_gregorian(self, vals_list):
        """
        Convert Jalali date strings in vals_list to Gregorian.
        
        Args:
            vals_list: List of dictionaries containing field values
        """
        for vals in vals_list:
            # Convert Date fields
            for field_name in self._jalaali_date_fields:
                if field_name in vals and vals[field_name]:
                    jalali_date = vals[field_name]
                    if self._is_jalali_format(jalali_date):
                        gregorian_date = self._jalali_to_gregorian(jalali_date)
                        vals[field_name] = gregorian_date
            
            # Convert Datetime fields
            for field_name in self._jalaali_datetime_fields:
                if field_name in vals and vals[field_name]:
                    jalali_datetime = vals[field_name]
                    if self._is_jalali_format(jalali_datetime, is_datetime=True):
                        gregorian_datetime = self._jalali_to_gregorian(
                            jalali_datetime, 
                            is_datetime=True
                        )
                        vals[field_name] = gregorian_datetime
    
    def _is_jalali_format(self, date_str, is_datetime=False):
        """
        Check if a date string is in Jalali format (YYYY-MM-DD).
        
        Jalali years are typically 1300-1500, while Gregorian are 1900-2100.
        """
        if not date_str or not isinstance(date_str, str):
            return False
        
        # Pattern for YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
        pattern = r'^(\d{4})-(\d{2})-(\d{2})'
        if is_datetime:
            pattern += r'(\s+\d{2}:\d{2}:\d{2})?$'
        else:
            pattern += '$'
        
        match = re.match(pattern, date_str)
        if not match:
            return False
        
        year = int(match.group(1))
        # Jalali years are typically between 1300 and 1500
        return 1300 <= year <= 1500
    
    def _jalali_to_gregorian(self, jalali_date, is_datetime=False):
        """
        Convert Jalali date to Gregorian using algorithm.
        
        Args:
            jalali_date: String in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
            is_datetime: Whether the input includes time
            
        Returns:
            String in Gregorian format
        """
        try:
            if is_datetime:
                date_part, time_part = jalali_date.split(' ')
            else:
                date_part = jalali_date
                time_part = None
            
            jy, jm, jd = map(int, date_part.split('-'))
            
            # Jalali to Gregorian conversion algorithm
            gy_days = (
                365 * ((jy - 1) // 33) * 33 +
                ((jy - 1) % 33) * 365 +
                ((jy - 1) // 33) * 8 +
                ((jy - 1) % 33 + 3) // 4
            )
            
            # Days in previous months
            month_days = [0, 31, 62, 93, 124, 155, 186, 217, 248, 279, 310, 341]
            gy_days += month_days[jm - 1] + jd - 1
            
            # Adjust for leap years
            if jm > 2 and ((jy - 1) % 33 == 3 or ((jy - 1) % 33 == 7 and (jy - 1) % 132 == 7)):
                gy_days += 1
            
            # Convert to Gregorian
            gy = 621 + (gy_days // 365)
            remaining_days = gy_days % 365
            
            # Adjust for Gregorian leap years
            leap_adjust = (gy // 4) - (gy // 100) + (gy // 400) - 153
            gy_days_adjusted = gy_days - leap_adjust
            
            # Calculate Gregorian month and day
            gm = 1
            gd = remaining_days + 1
            
            month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
                month_lengths[1] = 29
            
            while gd > month_lengths[gm - 1]:
                gd -= month_lengths[gm - 1]
                gm += 1
            
            result = f"{gy:04d}-{gm:02d}-{gd:02d}"
            if time_part:
                result += f" {time_part}"
            
            return result
        except Exception as e:
            raise ValidationError(f"Invalid Jalali date format: {jalali_date}. Error: {str(e)}")
    
    def _gregorian_to_jalali(self, gregorian_date, is_datetime=False):
        """
        Convert Gregorian date to Jalali.
        
        Args:
            gregorian_date: String in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
            is_datetime: Whether the input includes time
            
        Returns:
            String in Jalali format
        """
        try:
            if is_datetime:
                date_part, time_part = gregorian_date.split(' ')
            else:
                date_part = gregorian_date
                time_part = None
            
            gy, gm, gd = map(int, date_part.split('-'))
            
            # Gregorian to Jalali conversion algorithm
            gy_days = (
                365 * gy +
                ((gy + 3) // 4) -
                ((gy + 99) // 100) +
                ((gy + 399) // 400)
            )
            
            # Days in previous months
            month_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
            gy_days += month_days[gm - 1] + gd
            
            # Adjust for leap year
            if gm > 2 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
                gy_days += 1
            
            # Convert to Jalali
            jy = -621 + (gy_days // 365)
            remaining_days = gy_days % 365
            
            # Adjust for Jalali leap years
            leap_year = (jy % 33 == 1 or (jy % 33 == 5 and jy % 132 != 53))
            if remaining_days >= 365 - (1 if leap_year else 0):
                jy += 1
                remaining_days = 0
            
            # Calculate Jalali month and day
            jm = 1
            jd = remaining_days + 1
            
            # First 6 months have 31 days, next 5 have 30, last has 29 or 30
            if jd <= 186:
                jm = (jd - 1) // 31 + 1
                jd = (jd - 1) % 31 + 1
            else:
                jd -= 186
                jm = 7 + (jd - 1) // 30
                jd = (jd - 1) % 30 + 1
            
            result = f"{jy:04d}-{jm:02d}-{jd:02d}"
            if time_part:
                result += f" {time_part}"
            
            return result
        except Exception as e:
            raise ValidationError(f"Invalid Gregorian date format: {gregorian_date}. Error: {str(e)}")


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    use_jalaali_calendar = fields.Boolean(
        string="Use Jalali Calendar",
        default=False,
        help="Enable automatic Jalali date display and input for this user"
    )


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    use_jalaali_calendar = fields.Boolean(
        string="Use Jalali Calendar",
        default=False,
        help="Enable automatic Jalali date display and input for this company"
    )
