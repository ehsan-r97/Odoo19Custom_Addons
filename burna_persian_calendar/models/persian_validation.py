# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class PersianCalendarValidation(models.AbstractModel):
    """Abstract model to add server-side validation for Jalali dates.
    
    This ensures that dates entered via API, CSV imports, or other non-UI
    methods are properly validated before being stored in the database.
    
    Usage:
        Inherit this mixin in your model to enable Jalali date validation:
        
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['persian.calendar.validation']
            
            my_date = fields.Char()  # Store Jalali date as string
            
            @api.constrains('my_date')
            def _check_my_date(self):
                for record in self:
                    if record.my_date and not record._validate_jalali_date(record.my_date):
                        raise ValidationError(_("Invalid Jalali date: %s") % record.my_date)
    """
    _name = 'persian.calendar.validation'
    _description = 'Persian Calendar Validation Mixin'

    def _validate_jalali_date(self, jalali_str):
        """Validate a Jalali date string (YYYY-MM-DD format).
        
        Args:
            jalali_str: String in YYYY-MM-DD or YYYY/MM/DD format
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not jalali_str:
            return True
            
        # Normalize separators
        normalized = jalali_str.strip().replace('/', '-')
        
        # Check format
        if not re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', normalized):
            return False
        
        try:
            year, month, day = map(int, normalized.split('-'))
        except ValueError:
            return False
        
        # Validate ranges
        if year < 1300 or year > 1500:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        
        # Validate day for specific months
        if month > 6 and day > 30:
            return False
        if month == 12 and day > 29:
            # Check leap year
            if not self._is_jalali_leap_year(year):
                return False
        
        return True

    def _is_jalali_leap_year(self, year):
        """Check if a Jalali year is a leap year."""
        breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 
                  1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]
        
        if year < breaks[0] or year >= breaks[-1]:
            raise ValidationError(f"Invalid Jalali year {year}")
        
        jp = breaks[0]
        leapJ = -14
        
        for i in range(1, len(breaks)):
            jm = breaks[i]
            jump = jm - jp
            if year < jm:
                break
            leapJ = leapJ + (jump // 33) * 8 + ((jump % 33) // 4)
            jp = jm
        
        n = year - jp
        leapJ = leapJ + (n // 33) * 8 + ((n % 33) + 3) // 4
        
        if (jump % 33) == 4 and (jump - n) == 4:
            leapJ += 1
        
        leap = (((n + 1) % 33) - 1) % 4
        if leap == -1:
            leap = 4
        
        return leap == 0

    def _jalali_to_gregorian(self, jy, jm, jd):
        """Convert Jalali date to Gregorian."""
        def jal_cal(jy):
            breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 
                      1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]
            
            if jy < breaks[0] or jy >= breaks[-1]:
                raise ValidationError(f"Invalid Jalali year {jy}")
            
            gy = jy + 621
            leapJ = -14
            jp = breaks[0]
            
            for i in range(1, len(breaks)):
                jm_break = breaks[i]
                jump = jm_break - jp
                if jy < jm_break:
                    break
                leapJ = leapJ + (jump // 33) * 8 + ((jump % 33) // 4)
                jp = jm_break
            
            n = jy - jp
            leapJ = leapJ + (n // 33) * 8 + ((n % 33) + 3) // 4
            
            if (jump % 33) == 4 and (jump - n) == 4:
                leapJ += 1
            
            leapG = (gy // 4) - (((gy // 100) + 1) * 3 // 4) - 150
            march = 20 + leapJ - leapG
            
            if (jump - n) < 6:
                n = n - jump + ((jump + 4) // 33) * 33
            
            leap = (((n + 1) % 33) - 1) % 4
            if leap == -1:
                leap = 4
            
            return {'leap': leap, 'gy': gy, 'march': march}
        
        def g2d(gy, gm, gd):
            d = ((gy + ((gm - 8) // 6) + 100100) * 1461) // 4
            d += (153 * ((gm + 9) % 12) + 2) // 5
            d += gd - 34840408
            d -= (((gy + 100100 + ((gm - 8) // 6)) // 100) * 3) // 4 + 752
            return d
        
        def d2g(jdn):
            j = 4 * jdn + 139361631
            j += ((((4 * jdn + 183187720) // 146097) * 3) // 4) * 4 - 3908
            i = ((j % 1461) // 4) * 5 + 308
            gd = ((i % 153) // 5) + 1
            gm = ((i // 153) % 12) + 1
            gy = (j // 1461) - 100100 + ((8 - gm) // 6)
            return {'gy': gy, 'gm': gm, 'gd': gd}
        
        def j2d(jy, jm, jd):
            r = jal_cal(jy)
            return g2d(r['gy'], 3, r['march']) + (jm - 1) * 31 - (jm // 7) * (jm - 7) + jd - 1
        
        jdn = j2d(jy, jm, jd)
        g = d2g(jdn)
        return (g['gy'], g['gm'], g['gd'])

    def _gregorian_to_jalali(self, gy, gm, gd):
        """Convert Gregorian date to Jalali."""
        def jal_cal(jy):
            breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 
                      1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]
            
            if jy < breaks[0] or jy >= breaks[-1]:
                raise ValidationError(f"Invalid Jalali year {jy}")
            
            gy_calc = jy + 621
            leapJ = -14
            jp = breaks[0]
            
            for i in range(1, len(breaks)):
                jm_break = breaks[i]
                jump = jm_break - jp
                if jy < jm_break:
                    break
                leapJ = leapJ + (jump // 33) * 8 + ((jump % 33) // 4)
                jp = jm_break
            
            n = jy - jp
            leapJ = leapJ + (n // 33) * 8 + ((n % 33) + 3) // 4
            
            if (jump % 33) == 4 and (jump - n) == 4:
                leapJ += 1
            
            leapG = (gy_calc // 4) - (((gy_calc // 100) + 1) * 3 // 4) - 150
            march = 20 + leapJ - leapG
            
            if (jump - n) < 6:
                n = n - jump + ((jump + 4) // 33) * 33
            
            leap = (((n + 1) % 33) - 1) % 4
            if leap == -1:
                leap = 4
            
            return {'leap': leap, 'gy': gy_calc, 'march': march}
        
        def g2d(gy, gm, gd):
            d = ((gy + ((gm - 8) // 6) + 100100) * 1461) // 4
            d += (153 * ((gm + 9) % 12) + 2) // 5
            d += gd - 34840408
            d -= (((gy + 100100 + ((gm - 8) // 6)) // 100) * 3) // 4 + 752
            return d
        
        def d2j(jdn):
            gy_out, gm_out, gd_out = self._julian_to_gregorian(jdn)
            jy = gy_out - 621
            r = jal_cal(jy)
            julian1F = g2d(r['gy'], 3, r['march'])
            
            k = jdn - julian1F
            if k >= 0:
                if k <= 185:
                    return {'year': jy, 'month': 1 + k // 31, 'day': (k % 31) + 1}
                else:
                    k -= 186
            else:
                jy -= 1
                k += 179
                if r['leap'] == 1:
                    k += 1
            
            return {'year': jy, 'month': 7 + k // 30, 'day': (k % 30) + 1}
        
        jdn = g2d(gy, gm, gd)
        j = d2j(jdn)
        return (j['year'], j['month'], j['day'])

    def _julian_to_gregorian(self, julian):
        """Convert Julian day number to Gregorian date."""
        j = 4 * julian + 139361631
        j = j + (((4 * julian + 183187720) // 146097) * 3) // 4 * 4 - 3908
        
        i = ((j % 1461) // 4) * 5 + 308
        gd = ((i % 153) // 5) + 1
        gm = ((i // 153) % 12) + 1
        gy = (j // 1461) - 100100 + ((8 - gm) // 6)
        
        return {'year': gy, 'month': gm, 'day': gd}
