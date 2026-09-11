# -*- coding: utf-8 -*-
from odoo.tests import common, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestPersianCalendarValidation(common.TransactionCase):
    """Test suite for Persian Calendar validation logic."""

    def setUp(self):
        super().setUp()
        self.validation_model = self.env['persian.calendar.validation']

    def test_validate_valid_jalali_dates(self):
        """Test validation of valid Jalali dates."""
        # Valid dates in different formats
        valid_dates = [
            '1403-01-01',  # Farvardin 1, 1403
            '1403-06-31',  # Shahrivar 31 (last day of 6th month)
            '1403-07-30',  # Mehr 30 (30-day month)
            '1403-12-29',  # Esfand 29 (leap year)
            '1300-01-01',  # Minimum year
            '1500-12-29',  # Maximum year
        ]
        
        for date_str in valid_dates:
            result = self.validation_model._validate_jalali_date(date_str)
            self.assertTrue(result, f"Date {date_str} should be valid")

    def test_validate_invalid_jalali_dates(self):
        """Test validation of invalid Jalali dates."""
        # Invalid dates
        invalid_dates = [
            '9999-99-99',   # Invalid format/values
            '1403-13-01',   # Invalid month (>12)
            '1403-00-01',   # Invalid month (<1)
            '1403-01-00',   # Invalid day (<1)
            '1403-01-32',   # Invalid day (>31)
            '1403-07-31',   # Invalid day for 30-day month
            '1403-12-30',   # Invalid day for Esfand (non-leap)
            '1200-01-01',   # Year too low
            '1600-01-01',   # Year too high
            'invalid',       # Non-date string
            '',              # Empty string (should pass as True)
        ]
        
        for date_str in invalid_dates:
            if date_str == '':
                continue  # Empty string is considered valid (True)
            result = self.validation_model._validate_jalali_date(date_str)
            self.assertFalse(result, f"Date {date_str} should be invalid")

    def test_jalali_leap_year_detection(self):
        """Test Jalali leap year detection."""
        # Known leap years
        leap_years = [1399, 1403, 1407, 1411]
        for year in leap_years:
            result = self.validation_model._is_jalali_leap_year(year)
            self.assertTrue(result, f"Year {year} should be a leap year")
        
        # Known non-leap years
        non_leap_years = [1400, 1401, 1402, 1404]
        for year in non_leap_years:
            result = self.validation_model._is_jalali_leap_year(year)
            self.assertFalse(result, f"Year {year} should not be a leap year")

    def test_jalali_to_gregorian_conversion(self):
        """Test conversion from Jalali to Gregorian."""
        # Test known conversions
        test_cases = [
            ((1403, 1, 1), (2024, 3, 20)),  # Nowruz 1403
            ((1400, 1, 1), (2021, 3, 21)),  # Nowruz 1400
        ]
        
        for jalali, expected_gregorian in test_cases:
            result = self.validation_model._jalali_to_gregorian(*jalali)
            self.assertEqual(result, expected_gregorian, 
                           f"Conversion of {jalali} should be {expected_gregorian}")
