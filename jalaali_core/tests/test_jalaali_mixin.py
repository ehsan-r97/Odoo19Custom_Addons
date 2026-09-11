# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests import common
from odoo.exceptions import ValidationError

class TestModel(common.Model):
    _name = 'test.jalaali.model'
    _inherit = ['jalaali.mixin']
    
    name = fields.Char(required=True)
    meeting_date = fields.Date()
    meeting_time = fields.Datetime()
    
    _jalaali_date_fields = ['meeting_date']
    _jalaali_datetime_fields = ['meeting_time']


class TestJalaaliMixin(common.TransactionCase):
    """Test Jalali mixin auto-conversion."""
    
    def setUp(self):
        super().setUp()
        self.test_model = self.env['test.jalaali.model']
    
    def test_create_with_jalali_date(self):
        """Test creating record with Jalali date."""
        record = self.test_model.create({
            'name': 'Test Meeting',
            'meeting_date': '1403-01-15',  # Jalali date
        })
        
        # Should be converted to Gregorian
        self.assertTrue(record.meeting_date.startswith('2024'))
    
    def test_create_with_jalali_datetime(self):
        """Test creating record with Jalali datetime."""
        record = self.test_model.create({
            'name': 'Test Event',
            'meeting_time': '1403-01-15 14:30:00',
        })
        
        # Should be converted to Gregorian with time preserved
        self.assertIn(' ', record.meeting_time)
        self.assertIn('14:30:00', record.meeting_time)
    
    def test_write_with_jalali_date(self):
        """Test updating record with Jalali date."""
        record = self.test_model.create({
            'name': 'Test Update',
            'meeting_date': '2024-04-03',  # Gregorian initially
        })
        
        # Update with Jalali date
        record.write({'meeting_date': '1403-01-15'})
        
        # Should be converted to Gregorian
        self.assertTrue(record.meeting_date.startswith('2024'))
    
    def test_create_with_gregorian_date(self):
        """Test that Gregorian dates pass through unchanged."""
        record = self.test_model.create({
            'name': 'Test Gregorian',
            'meeting_date': '2024-04-03',
        })
        
        self.assertEqual(record.meeting_date, '2024-04-03')
    
    def test_invalid_jalali_in_create(self):
        """Test invalid Jalali date in create raises error."""
        with self.assertRaises(ValidationError):
            self.test_model.create({
                'name': 'Invalid',
                'meeting_date': '1403-13-45',  # Invalid month and day
            })
