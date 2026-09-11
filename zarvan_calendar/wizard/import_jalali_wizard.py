# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_utils
import base64
import io
import csv
from datetime import datetime
import jdatetime


class ImportJalaliWizard(models.TransientModel):
    """
    Wizard to import CSV/Excel files with Jalali dates.
    
    Features:
    - Auto-detect Jalali vs Gregorian dates
    - Validate all dates before import
    - Show preview of converted dates
    - Error reporting for invalid rows
    """
    _name = 'jalaali.import.wizard'
    _description = 'Import Jalali Dates Wizard'

    file = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")
    
    model_id = fields.Many2one(
        'ir.model',
        string="Model",
        required=True,
        domain=[('transient', '=', False)],
        help="Select the model to import data into"
    )
    
    date_field = fields.Char(
        string="Date Field",
        required=True,
        help="Name of the date field in the model (e.g., 'date', 'invoice_date')"
    )
    
    has_header = fields.Boolean(string="File has header row", default=True)
    
    # Preview data
    preview_data = fields.Text(string="Preview", readonly=True)
    total_rows = fields.Integer(string="Total Rows", readonly=True)
    valid_rows = fields.Integer(string="Valid Rows", readonly=True)
    invalid_rows = fields.Integer(string="Invalid Rows", readonly=True)
    
    state = fields.Selection([
        ('draft', 'Select File'),
        ('preview', 'Preview'),
        ('done', 'Done'),
    ], default='draft')

    def _jalali_to_gregorian(self, jalali_str):
        """Convert Jalali string to Gregorian date."""
        try:
            normalized = jalali_str.replace('/', '-')
            parts = normalized.split('-')
            if len(parts) != 3:
                return None
            
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            j_date = jdatetime.date(year, month, day)
            g_date = j_date.togregorian()
            return g_date.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            return None

    def _detect_date_format(self, date_str):
        """Detect if date string is Jalali or Gregorian."""
        try:
            normalized = date_str.replace('/', '-')
            parts = normalized.split('-')
            if len(parts) != 3:
                return None, None
            
            year = int(parts[0])
            if year > 1300:
                return 'jalali', date_str
            elif year >= 1900:
                return 'gregorian', date_str
            return None, None
        except (ValueError, AttributeError):
            return None, None

    def action_preview(self):
        """Parse file and show preview of conversions."""
        self.ensure_one()
        
        if not self.file:
            raise ValidationError(_("Please select a file to import."))
        
        # Decode file
        file_content = base64.b64decode(self.file)
        
        # Try to parse as CSV
        try:
            # Try different encodings
            decoded = None
            for encoding in ['utf-8', 'cp1256', 'iso-8859-1']:
                try:
                    decoded = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if not decoded:
                raise ValidationError(_("Unable to decode file. Please ensure it's UTF-8 encoded."))
            
            lines = decoded.strip().split('\n')
            reader = csv.reader(lines)
            rows = list(reader)
            
            if not rows:
                raise ValidationError(_("File is empty."))
            
            # Skip header if present
            start_idx = 1 if self.has_header else 0
            data_rows = rows[start_idx:]
            
            self.total_rows = len(data_rows)
            valid_count = 0
            invalid_count = 0
            preview_lines = []
            
            # Process first 10 rows for preview
            for i, row in enumerate(data_rows[:10]):
                if len(row) == 0:
                    continue
                
                # Find date column (simplified - assumes first date-like field)
                date_val = None
                for cell in row:
                    fmt, val = self._detect_date_format(cell)
                    if fmt:
                        date_val = cell
                        break
                
                if date_val:
                    fmt, _ = self._detect_date_format(date_val)
                    if fmt == 'jalali':
                        gregorian = self._jalali_to_gregorian(date_val)
                        if gregorian:
                            valid_count += 1
                            preview_lines.append(f"Row {i+1}: {date_val} (Jalali) → {gregorian} (Gregorian) ✓")
                        else:
                            invalid_count += 1
                            preview_lines.append(f"Row {i+1}: {date_val} - Invalid Jalali date ✗")
                    else:
                        valid_count += 1
                        preview_lines.append(f"Row {i+1}: {date_val} (Gregorian) → No conversion needed ✓")
                else:
                    preview_lines.append(f"Row {i+1}: No date found")
            
            if len(data_rows) > 10:
                preview_lines.append(f"... and {len(data_rows) - 10} more rows")
            
            self.preview_data = '\n'.join(preview_lines)
            self.valid_rows = valid_count
            self.invalid_rows = invalid_count
            self.state = 'preview'
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
            
        except Exception as e:
            raise ValidationError(_("Error parsing file: %s") % str(e))

    def action_import(self):
        """Import the file after validation."""
        self.ensure_one()
        
        if self.state != 'preview':
            raise ValidationError(_("Please preview the file first."))
        
        # Decode file again
        file_content = base64.b64decode(self.file)
        decoded = None
        for encoding in ['utf-8', 'cp1256', 'iso-8859-1']:
            try:
                decoded = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if not decoded:
            raise ValidationError(_("Unable to decode file."))
        
        lines = decoded.strip().split('\n')
        reader = csv.DictReader(lines) if self.has_header else csv.reader(lines)
        
        Model = self.env[self.model_id.model]
        success_count = 0
        error_count = 0
        errors = []
        
        start_idx = 1 if self.has_header else 0
        data_lines = lines[start_idx:]
        
        for i, line in enumerate(data_lines):
            try:
                if self.has_header:
                    row_dict = next(csv.DictReader([line], fieldnames=reader.fieldnames))
                else:
                    row_parts = line.split(',')
                    row_dict = {f'field_{j}': val for j, val in enumerate(row_parts)}
                
                # Find and convert date field
                date_val = row_dict.get(self.date_field)
                if date_val:
                    fmt, _ = self._detect_date_format(date_val)
                    if fmt == 'jalali':
                        gregorian = self._jalali_to_gregorian(date_val)
                        if not gregorian:
                            errors.append(f"Row {i+1}: Invalid Jalali date '{date_val}'")
                            error_count += 1
                            continue
                        row_dict[self.date_field] = gregorian
                
                # Create record
                Model.create(row_dict)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
                error_count += 1
        
        # Show result
        message = _("Import completed successfully!\n\n")
        message += _("✓ Imported: %d records") % success_count
        if error_count > 0:
            message += _("\n✗ Failed: %d records") % error_count
            message += _("\n\nErrors:\n") + '\n'.join(errors[:10])
            if len(errors) > 10:
                message += _("\n... and %d more errors") % (len(errors) - 10)
        
        self.preview_data = message
        self.state = 'done'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reset(self):
        """Reset wizard to initial state."""
        self.write({
            'file': False,
            'filename': False,
            'preview_data': False,
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
