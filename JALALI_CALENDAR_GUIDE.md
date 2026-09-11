# Jalali Calendar Modules for Odoo 19 - Complete Guide

## 📦 Module Overview

### 1. **burna_persian_calendar** - Form/List/Kanban Support
- Full Jalali date picker in forms
- Jalali dates in list and kanban views  
- Server-side validation for imports/API
- **Fixed Issues:** Asset loading order, redundant libraries, missing validation

### 2. **burna_calendar** - Calendar View Support  
- Jalali dates in calendar widget
- Shamsi month/day names
- **Fixed Issues:** Performance (DOM observer scope), input corruption

---

## 🚀 Installation & Usage

### Step 1: Install Modules
```bash
# Copy modules to your Odoo addons path
cp -r burna_persian_calendar /path/to/odoo/addons/
cp -r burna_calendar /path/to/odoo/addons/

# Update app list in Odoo
Settings → Apps → Update Apps List

# Install both modules
Settings → Apps → Search "Persian Calendar" → Install
Settings → Apps → Search "گاهشمار برنا" → Install
```

### Step 2: Configure User Language
```
Settings → Users & Companies → Users → Select User
Set Language to: Persian (Iran) / فارسی (ایران)
Save
```

---

## 📝 Using in Forms (OWL Components)

### Method 1: Standard Date Fields (Automatic)
```python
# In your model
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['persian.calendar.validation']  # For validation
    
    meeting_date = fields.Date(string="Meeting Date")
    start_datetime = fields.Datetime(string="Start Time")
```

```xml
<!-- In your form view - No special widget needed! -->
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="meeting_date"/>  <!-- Shows Jalali picker automatically -->
                    <field name="start_datetime"/>  <!-- Shows Jalali datetime picker -->
                </group>
            </sheet>
        </form>
    </field>
</record>
```

### Method 2: Custom OWL Component with Validation
```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class JalaliDateField extends Component {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        // Props: value (Jalali date string), onChange callback
        this.jalaliValue = this.props.value || "";
    }

    async onDateChange(ev) {
        const jalaliDate = ev.target.value;  // Format: 1403-01-15
        
        // Validate on server before saving
        try {
            await this.rpc('/web/dataset/call_kw', {
                model: 'persian.calendar.validation',
                method: '_validate_jalali_date',
                args: [jalaliDate],
                kwargs: {},
            });
            
            this.jalaliValue = jalaliDate;
            this.props.onChange(jalaliDate);
        } catch (error) {
            this.notification.add("Invalid Jalali date format", {
                type: "danger",
            });
        }
    }
}

JalaliDateField.template = "my_module.JalaliDateField";
JalaliDateField.props = ["value", "onChange"];

registry.category("fields").add("jalali_date", JalaliDateField);
```

```xml
<!-- Template -->
<template t-name="my_module.JalaliDateField">
    <input 
        type="text" 
        t-att-value="state.jalaliValue"
        t-on-change="onDateChange"
        placeholder="1403-01-01"
        class="form-control"
    />
</template>
```

---

## 📊 Excel/CSV Import with Jalali Dates

### Option 1: Using Validation Mixin (Recommended)

```python
# In your model
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Invoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'persian.calendar.validation']
    
    jalali_invoice_date = fields.Char(string="Invoice Date (Jalali)")
    
    @api.constrains('jalali_invoice_date')
    def _check_jalali_invoice_date(self):
        for record in self:
            if record.jalali_invoice_date:
                if not record._validate_jalali_date(record.jalali_invoice_date):
                    raise ValidationError(_(
                        "Invalid Jalali date: %s. Expected format: YYYY-MM-DD"
                    ) % record.jalali_invoice_date)
    
    @api.onchange('jalali_invoice_date')
    def _onchange_jalali_invoice_date(self):
        """Auto-convert Jalali to Gregorian for storage"""
        if self.jalali_invoice_date:
            parts = self.jalali_invoice_date.replace('/', '-').split('-')
            if len(parts) == 3:
                jy, jm, jd = map(int, parts)
                gy, gm, gd = self._jalali_to_gregorian(jy, jm, jd)
                self.invoice_date = f"{gy}-{gm:02d}-{gd:02d}"
```

### Option 2: Import Wizard with Conversion

```python
# wizards/jalali_import_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import csv
from io import StringIO

class JalaliImportWizard(models.TransientModel):
    _name = 'jalali.import.wizard'
    _description = 'Import Data with Jalali Dates'
    
    file = fields.Binary(string="CSV File", required=True)
    filename = fields.Char(string="Filename")
    model_name = fields.Char(string="Model", required=True)
    
    def action_import(self):
        """Import CSV with Jalali date conversion"""
        self.ensure_one()
        
        # Decode file
        file_content = base64.b64decode(self.file)
        csv_content = file_content.decode('utf-8')
        reader = csv.DictReader(StringIO(csv_content))
        
        Model = self.env[self.model_name]
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Convert Jalali dates to Gregorian
                converted_row = {}
                for field_name, value in row.items():
                    if 'date' in field_name.lower() and value:
                        # Try to parse as Jalali
                        if self._is_jalali_format(value):
                            jy, jm, jd = self._parse_jalali(value)
                            gy, gm, gd = Model._jalali_to_gregorian(jy, jm, jd)
                            converted_row[field_name] = f"{gy}-{gm:02d}-{gd:02d}"
                        else:
                            converted_row[field_name] = value
                    else:
                        converted_row[field_name] = value
                
                # Create record
                Model.create(converted_row)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        if errors:
            raise ValidationError("\n".join(errors))
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}
    
    def _is_jalali_format(self, value):
        """Check if value looks like Jalali date"""
        import re
        return bool(re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$', value))
    
    def _parse_jalali(self, value):
        """Parse Jalali date string"""
        parts = value.replace('/', '-').split('-')
        return map(int, parts)
```

```xml
<!-- Wizard View -->
<record id="view_jalali_import_wizard_form" model="ir.ui.view">
    <field name="name">jalali.import.wizard.form</field>
    <field name="model">jalali.import.wizard</field>
    <field name="arch" type="xml">
        <form string="Import Jalali Data">
            <group>
                <field name="file"/>
                <field name="filename" invisible="1"/>
                <field name="model_name"/>
            </group>
            <footer>
                <button string="Import" type="object" name="action_import" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>

<!-- Action -->
<record id="action_jalali_import_wizard" model="ir.actions.act_window">
    <field name="name">Import with Jalali Dates</field>
    <field name="res_model">jalali.import.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>
```

### CSV File Format Example
```csv
name,jalali_invoice_date,amount
"Test Invoice 1",1403-01-15,1000000
"Test Invoice 2",1403-02-20,2500000
"Test Invoice 3",1403/03/25,750000
```

---

## 🔧 Advanced: Custom Validation Rules

```python
# Add custom constraints in your model
class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'persian.calendar.validation']
    
    planned_date_jalali = fields.Char(string="Planned Date (Jalali)")
    
    @api.constrains('planned_date_jalali')
    def _check_planned_date_range(self):
        for task in self:
            if task.planned_date_jalali:
                parts = task.planned_date_jalali.split('-')
                year = int(parts[0])
                
                # Ensure date is within reasonable range
                if year < 1400 or year > 1410:
                    raise ValidationError(_(
                        "Planned date must be between 1400 and 1410"
                    ))
                
                # Check it's not in the past
                jy, jm, jd = map(int, parts)
                gy, gm, gd = task._jalali_to_gregorian(jy, jm, jd)
                from datetime import date
                if date(gy, gm, gd) < date.today():
                    raise ValidationError(_(
                        "Planned date cannot be in the past"
                    ))
```

---

## 🧪 Testing

Run tests:
```bash
./odoo-bin -c odoo.conf -u burna_persian_calendar --test-enable
```

Test validation manually:
```python
# In Odoo shell
env['persian.calendar.validation']._validate_jalali_date('1403-01-15')  # True
env['persian.calendar.validation']._validate_jalali_date('1403-13-01')  # False
env['persian.calendar.validation']._is_jalali_leap_year(1403)  # True
env['persian.calendar.validation']._jalali_to_gregorian(1403, 1, 1)  # (2024, 3, 20)
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Date picker not showing Jalali
**Solution:** Ensure user language is set to Persian (Iran)

### Issue 2: CSV import fails with invalid dates
**Solution:** Use the validation mixin and check date format (YYYY-MM-DD)

### Issue 3: Calendar view shows Gregorian
**Solution:** Verify `burna_calendar` module is installed and assets loaded

### Issue 4: Assets not loading in correct order
**Solution:** Fixed in v19.0.2.0.0 - JDate utils now loads first

---

## 📚 API Reference

### Server-side Methods

| Method | Description | Example |
|--------|-------------|---------|
| `_validate_jalali_date(date_str)` | Validate Jalali date string | `_validate_jalali_date('1403-01-15')` → `True` |
| `_is_jalali_leap_year(year)` | Check leap year | `_is_jalali_leap_year(1403)` → `True` |
| `_jalali_to_gregorian(jy, jm, jd)` | Convert to Gregorian | `_jalali_to_gregorian(1403, 1, 1)` → `(2024, 3, 20)` |
| `_gregorian_to_jalali(gy, gm, gd)` | Convert to Jalali | `_gregorian_to_jalali(2024, 3, 20)` → `(1403, 1, 1)` |

### Client-side (JDate)

```javascript
// Create JDate instance
const jDate = new JDate();  // Current date
const jDate2 = new JDate('1403/01/15');  // Parse string

// Get components
jDate.getFullYear();  // 1403
jDate.getMonth();     // 1 (Farvardin)
jDate.getDate();      // 15

// Format
jDate.format('YYYY/MM/DD');  // "1403/01/15"
jDate.format('dddd DD MMMM YYYY');  // "دوشنبه 15 فروردین 1403"

// Convert
JDate.Utils.toJalali(new Date(2024, 2, 20));  // {year: 1403, month: 1, date: 1}
JDate.Utils.toGregorian(1403, 1, 1);  // {year: 2024, month: 3, date: 20}

// Arithmetic
jDate.add('month', 1);      // Next month
jDate.subtract('day', 7);   // Previous week
```

---

## 🎯 Best Practices

1. **Always inherit validation mixin** for models with Jalali date fields
2. **Store dates as Gregorian** in database, display as Jalali in UI
3. **Use standard Date/Datetime fields** - no need for Char fields
4. **Validate on both client and server** for imports/API calls
5. **Test with leap years** (1399, 1403, 1407, etc.)

---

## 📄 License
LGPL-3.0 - See LICENSE files in each module

## 👥 Credits
- Odoo Community Iran (https://odoo-community.ir/)
- Burna Dev (https://www.burna.ir)
