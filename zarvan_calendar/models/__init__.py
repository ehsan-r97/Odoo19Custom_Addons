# -*- coding: utf-8 -*-
from odoo import models, fields, api
import functools

try:
    import jdatetime
except ImportError:
    jdatetime = None

class ZarvanMixin(models.AbstractModel):
    _name = 'zarvan.calendar.mixin'
    _description = 'Zarvan Calendar Mixin for Jalali Conversion'

    @api.model
    @functools.lru_cache(maxsize=1024)
    def _gregorian_to_jalali(self, g_date_str):
        """Convert Gregorian date string to Jalali. Cached for performance."""
        if not g_date_str or not jdatetime:
            return g_date_str
        try:
            g_obj = jdatetime.date.fromisoformat(g_date_str) if isinstance(g_date_str, str) else g_date_str
            j_obj = jdatetime.date.fromgregorian(date=g_obj)
            return j_obj.strftime('%Y/%m/%d')
        except Exception:
            return g_date_str

    @api.model
    @functools.lru_cache(maxsize=1024)
    def _jalali_to_gregorian(self, j_date_str):
        """Convert Jalali date string to Gregorian. Cached for performance."""
        if not j_date_str or not jdatetime:
            return j_date_str
        try:
            # Simple format YYYY/MM/DD or YYYY-MM-DD
            parts = j_date_str.replace('-', '/').split('/')
            if len(parts) == 3:
                j_obj = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                g_obj = j_obj.togregorian()
                return g_obj.strftime('%Y-%m-%d')
        except Exception:
            pass
        return j_date_str

    def _parse_persian_nlp(self, text):
        """
        Safe, rule-based Persian NLP parser.
        Supports: امروز، فردا، شنبه آینده، جمعه گذشته، هفته پیش، ماه بعد
        Returns Gregorian date string or None.
        """
        if not text or not isinstance(text, str):
            return None
        if not jdatetime:
            return None
            
        today = jdatetime.date.today().togregorian()
        text = text.strip()
        
        # Simple direct matches
        if text == 'امروز':
            return today.strftime('%Y-%m-%d')
        elif text == 'فردا':
            return (today + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        elif text == 'دیروز':
            return (today - jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
        # Day of week logic (simplified for safety)
        days_fa = {'شنبه': 5, 'یکشنبه': 6, 'دوشنبه': 0, 'سه‌شنبه': 1, 'چهارشنبه': 2, 'پنجشنبه': 3, 'جمعه': 4}
        # Note: Python weekday(): Monday=0, Sunday=6. Iranian: Shanbeh=Saturday (end of week)
        # Mapping adjusted for standard Python weekday calculation relative to Saturday
        
        current_weekday = today.weekday() # Mon=0 ... Sun=6
        # Iranian week starts Saturday. 
        # Let's map target day to Python weekday
        # Shanbeh (Sat) -> 5, Yekshanbeh (Sun) -> 6, Doshanbeh (Mon) -> 0 ... Jomeh (Fri) -> 4
        
        target_day_map = {
            'شنبه': 5, 'یکشنبه': 6, 'دوشنبه': 0, 'سه‌شنبه': 1, 
            'چهارشنبه': 2, 'پنجشنبه': 3, 'جمعه': 4
        }
        
        for day_name, target_w in target_day_map.items():
            if day_name in text:
                direction = 0
                if 'آینده' in text or 'بعد' in text:
                    direction = 1
                elif 'گذشته' in text or 'پیش' in text:
                    direction = -1
                
                if direction != 0:
                    days_ahead = target_w - current_weekday
                    if direction == 1 and days_ahead <= 0:
                        days_ahead += 7
                    elif direction == -1 and days_ahead >= 0:
                        days_ahead -= 7
                    
                    target_date = today + jdatetime.timedelta(days=days_ahead)
                    return target_date.strftime('%Y-%m-%d')

        return None

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    enable_jalali_display = fields.Boolean(string="Show Dates in Jalali", default=False, help="Display dates in Persian (Jalali) calendar format.")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    jalali_default_for_new_users = fields.Boolean(
        string="Default Jalali for New Users",
        config_parameter='zarvan_calendar.default_jalali',
        help="New users will have Jalali display enabled by default."
    )
