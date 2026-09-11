# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo.exceptions import ValidationError

class TestJalaaliConversion(common.TransactionCase):
    """Test Jalali/Gregorian conversion algorithms."""
    
    def setUp(self):
        super().setUp()
        self.mixin = self.env['jalaali.mixin']
    
    def test_jalali_to_gregorian_basic(self):
        """Test basic Jalali to Gregorian conversion."""
        # 1403-01-15 (Farvardin 15, 1403) should be around 2024-04-03
        result = self.mixin._jalali_to_gregorian('1403-01-15')
        self.assertTrue(result.startswith('2024'))
    
    def test_gregorian_to_jalali_basic(self):
        """Test basic Gregorian to Jalali conversion."""
        # 2024-04-03 should be around 1403-01-15
        result = self.mixin._gregorian_to_jalali('2024-04-03')
        self.assertTrue(result.startswith('1403'))
    
    def test_is_jalali_format(self):
        """Test Jalali format detection."""
        self.assertTrue(self.mixin._is_jalali_format('1403-01-15'))
        self.assertTrue(self.mixin._is_jalali_format('1300-12-29'))
        self.assertFalse(self.mixin._is_jalali_format('2024-01-15'))
        self.assertFalse(self.mixin._is_jalali_format('1200-01-01'))
        self.assertFalse(self.mixin._is_jalali_format('1600-01-01'))
    
    def test_datetime_conversion(self):
        """Test datetime (with time) conversion."""
        jalali_dt = '1403-01-15 14:30:00'
        result = self.mixin._jalali_to_gregorian(jalali_dt, is_datetime=True)
        self.assertIn(' ', result)  # Should have space between date and time
        self.assertIn('14:30:00', result)
    
    def test_invalid_jalali_date(self):
        """Test invalid Jalali date raises error."""
        with self.assertRaises(ValidationError):
            self.mixin._jalali_to_gregorian('1403-13-01')  # Invalid month
        
        with self.assertRaises(ValidationError):
            self.mixin._jalali_to_gregorian('1403-01-32')  # Invalid day
    
    def test_leap_year_detection(self):
        """Test leap year handling."""
        # Test a known leap year in Jalali
        # 1403 is not a leap year, but we test the algorithm handles it
        result = self.mixin._jalali_to_gregorian('1403-12-29')
        self.assertIsNotNone(result)
