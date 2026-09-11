# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import float_utils

class JalaaliImportWizard(models.TransientModel):
    """
    Wizard for importing CSV/Excel files with Jalali dates.
    
    Usage:
        1. Go to Settings > Import Jalali Data
        2. Upload your CSV/Excel file
        3. Map columns (mark which ones contain Jalali dates)
        4. Preview converted data
        5. Import to target model
    """
    _name = 'jalaali.import.wizard'
    _description = 'Jalali Import Wizard'
    
    file_data = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")
    target_model_id = fields.Many2one('ir.model', string="Target Model", required=True)
    delimiter = fields.Selection([
        (',', 'Comma'),
        (';', 'Semicolon'),
        ('\t', 'Tab'),
    ], string="Delimiter", default=',')
    
    column_mapping = fields.Json(string="Column Mapping", default="{}")
    preview_data = fields.Text(string="Preview Data", readonly=True)
    has_errors = fields.Boolean(string="Has Errors", readonly=True)
    error_message = fields.Text(string="Error Message", readonly=True)
    
    def action_parse_file(self):
        """Parse uploaded file and show preview."""
        import csv
        import io
        
        if not self.file_data:
            raise ValueError("No file uploaded")
        
        # Decode file
        file_content = io.StringIO(self.file_data.decode('utf-8'))
        
        # Parse CSV
        reader = csv.DictReader(file_content, delimiter=self.delimiter)
        rows = list(reader)
        
        if not rows:
            raise ValueError("Empty file")
        
        # Get first 10 rows for preview
        preview_rows = []
        for i, row in enumerate(rows[:10]):
            preview_row = {}
            for field, value in row.items():
                preview_row[field] = value
            preview_rows.append(preview_row)
        
        self.preview_data = str(preview_rows)
        self.has_errors = False
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_import(self):
        """Import data after converting Jalali dates to Gregorian."""
        import csv
        import io
        
        if not self.file_data:
            raise ValueError("No file uploaded")
        
        # Get the mixin model for conversion
        mixin_model = self.env['jalaali.mixin']
        
        # Decode file
        file_content = io.StringIO(self.file_data.decode('utf-8'))
        
        # Parse CSV
        reader = csv.DictReader(file_content, delimiter=self.delimiter)
        rows = list(reader)
        
        # Convert Jalali dates and prepare records
        converted_rows = []
        errors = []
        
        for row_num, row in enumerate(rows, start=2):  # Start from 2 (header is row 1)
            try:
                converted_row = {}
                
                for field_name, value in row.items():
                    # Check if this field should be converted
                    if field_name in self.column_mapping.get('date_fields', []):
                        if value and mixin_model._is_jalali_format(value):
                            converted_row[field_name] = mixin_model._jalali_to_gregorian(value)
                        else:
                            converted_row[field_name] = value
                    elif field_name in self.column_mapping.get('datetime_fields', []):
                        if value and mixin_model._is_jalali_format(value, is_datetime=True):
                            converted_row[field_name] = mixin_model._jalali_to_gregorian(value, is_datetime=True)
                        else:
                            converted_row[field_name] = value
                    else:
                        converted_row[field_name] = value
                
                converted_rows.append(converted_row)
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        if errors:
            self.has_errors = True
            self.error_message = "\n".join(errors)
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        
        # Create records in target model
        target_model = self.env[self.target_model_id.model]
        
        # Check if target model inherits jalaali.mixin
        if 'jalaali.mixin' not in target_model._inherit:
            # If not, we need to manually convert
            for row in converted_rows:
                for field_name in self.column_mapping.get('date_fields', []):
                    if field_name in row and row[field_name]:
                        if mixin_model._is_jalali_format(row[field_name]):
                            row[field_name] = mixin_model._jalali_to_gregorian(row[field_name])
                
                for field_name in self.column_mapping.get('datetime_fields', []):
                    if field_name in row and row[field_name]:
                        if mixin_model._is_jalali_format(row[field_name], is_datetime=True):
                            row[field_name] = mixin_model._jalali_to_gregorian(row[field_name], is_datetime=True)
        
        # Create all records
        target_model.create(converted_rows)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Successfully imported {len(converted_rows)} records',
                'type': 'success',
                'sticky': False,
            }
        }
