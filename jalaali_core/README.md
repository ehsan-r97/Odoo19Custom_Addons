# Jalaali Core Utilities for Odoo 19

Complete Jalali (Persian) calendar support for Odoo 19 with automatic conversion, OWL components, and Excel/CSV import.

## Features

✅ **Server-Side Auto-Conversion** - Automatically converts Jalali dates to Gregorian on create/write
✅ **OWL Components** - Reusable Jalali date picker component for custom views
✅ **Excel/CSV Import Wizard** - Import data with Jalali dates directly
✅ **Per-User Configuration** - Enable/disable Jalali calendar per user or company
✅ **Comprehensive Tests** - Full test coverage for conversion algorithms
✅ **High Performance** - Optimized conversion algorithms

## Installation

1. Copy `jalaali_core` to your Odoo addons directory
2. Update apps list: Settings → Apps → Update Apps List
3. Install "Jalaali Core Utilities" module

## Usage

### 1. Automatic Conversion in Models

```python
from odoo import models, fields

class Invoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'jalaali.mixin']
    
    # Specify which fields contain Jalali dates
    _jalaali_date_fields = ['invoice_date_jalali']
    _jalaali_datetime_fields = ['invoice_datetime_jalali']
    
    invoice_date_jalali = fields.Date()
    invoice_datetime_jalali = fields.Datetime()
```

Now you can create records with Jalali dates:

```python
env['account.move'].create({
    'name': 'INV/2024/001',
    'invoice_date_jalali': '1403-01-15',  # Automatically converted to Gregorian
})
```

### 2. Using in OWL Components

```javascript
import { Component } from "@odoo/owl";
import { jalaali } from "@jalaali_core/lib/jalaali";

export class MyComponent extends Component {
    convertDate() {
        // Gregorian to Jalali
        const { jy, jm, jd } = jalaali.toJalaali(2024, 4, 3);
        console.log(jalaali.formatDate(jy, jm, jd)); // "1403-01-15"
        
        // Jalali to Gregorian
        const parsed = jalaali.parseDate("1403-01-15");
        const { gy, gm, gd } = jalaali.toGregorian(parsed.jy, parsed.jm, parsed.jd);
        console.log(jalaali.formatDate(gy, gm, gd)); // "2024-04-03"
    }
}
```

### 3. CSV/Excel Import

1. Go to **Settings → Import Jalali Data**
2. Upload your CSV file with Jalali dates
3. Select target model (e.g., Invoices, Partners)
4. Map columns and mark which contain Jalali dates
5. Preview converted data
6. Click Import

**CSV Format Example:**
```csv
name,date_jalali,amount
"Invoice 1",1403-01-15,1000000
"Invoice 2",1403-02-20,2500000
```

### 4. Custom Validation

```python
@api.constrains('birth_date')
def _check_birth_date(self):
    if not self.env['jalaali.mixin']._is_jalali_format(self.birth_date):
        raise ValidationError("Please enter a valid Jalali date (YYYY-MM-DD)")
```

## API Reference

### Server-Side (Python)

```python
mixin = env['jalaali.mixin']

# Check if string is Jalali format
is_jalali = mixin._is_jalali_format('1403-01-15')  # True
is_jalali_dt = mixin._is_jalali_format('1403-01-15 14:30:00', is_datetime=True)

# Convert Jalali to Gregorian
gregorian = mixin._jalali_to_gregorian('1403-01-15')  # "2024-04-03"
gregorian_dt = mixin._jalali_to_gregorian('1403-01-15 14:30:00', is_datetime=True)

# Convert Gregorian to Jalali
jalali = mixin._gregorian_to_jalali('2024-04-03')  # "1403-01-15"
```

### Client-Side (JavaScript)

```javascript
import { jalaali, jalaaliMonths, jalaaliDays } from "@jalaali_core/lib/jalaali";

// Convert Gregorian to Jalali
const { jy, jm, jd } = jalaali.toJalaali(2024, 4, 3);

// Convert Jalali to Gregorian
const { gy, gm, gd } = jalaali.toGregorian(1403, 1, 15);

// Parse and validate
const parsed = jalaali.parseDate("1403-01-15");  // { jy: 1403, jm: 1, jd: 15 } or null

// Format
const formatted = jalaali.formatDate(1403, 1, 15);  // "1403-01-15"
const custom = jalaali.formatDate(1403, 1, 15, "DD/MM/YYYY");  // "15/01/1403"

// Leap year check
const isLeap = jalaali.isLeapJalaali(1403);  // false

// Month/Day names
console.log(jalaaliMonths[0]);  // "Farvardin"
console.log(jalaaliDays[0]);    // "Saturday"
```

## Testing

Run tests with:

```bash
odoo-bin --test-enable --test-tags jalaali_core
```

Or via command:

```bash
./odoo-bin -d your_database --test-tags /jalaali_core:TestJalaaliConversion
```

## Configuration

Enable Jalali calendar for specific users or companies:

1. **Per User**: Go to Settings → Users → select user → Preferences tab → Check "Use Jalali Calendar"
2. **Per Company**: Go to Settings → Companies → select company → Check "Use Jalali Calendar"

## Troubleshooting

### Asset Loading Issues
If Jalali components don't load:
```bash
# Clear browser cache
# Or restart Odoo with -u flag
./odoo-bin -d your_database -u jalaali_core
```

### Conversion Errors
Check that dates are in correct format:
- Date: `YYYY-MM-DD` (e.g., `1403-01-15`)
- Datetime: `YYYY-MM-DD HH:MM:SS` (e.g., `1403-01-15 14:30:00`)

### Import Wizard Not Found
Ensure you have access rights:
- Go to Settings → Users → ensure user has "Internal User" access level

## License

LGPL-3

## Authors

Odoo Community Contributors
