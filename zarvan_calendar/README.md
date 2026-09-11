# Jalaali Pro - Professional Jalali Calendar for Odoo 19

## 📋 Overview

**Jalaali Pro** is a complete, production-ready Jalali (Persian/Shamsi) calendar solution for Odoo 19. It provides seamless bidirectional conversion between Jalali and Gregorian dates while maintaining data integrity.

### ✨ Key Features

- **Server-Side Conversion**: Python-based conversion using `jdatetime` library
- **Client-Side Display**: OWL components with real-time conversion
- **Hybrid Input**: Accepts both Jalali (1403-01-15) and Gregorian (2024-03-20) formats
- **Excel/CSV Import Wizard**: Validate and convert Jalali dates during import
- **Per-User Preferences**: Enable/disable Jalali calendar per user
- **Holiday Management**: Built-in Persian holiday database
- **Accessibility**: Full ARIA support and keyboard navigation
- **Comprehensive Tests**: Unit tests for all conversion logic

---

## 🚀 Installation

### Prerequisites

```bash
pip install jdatetime
```

### Steps

1. Copy `jalaali_pro` folder to your Odoo addons directory
2. Update apps list: **Apps → Update Apps List**
3. Install module: Search for "Jalaali Pro" and click Install
4. Configure user preferences: **Settings → Users → Preferences → Jalali Calendar Settings**

---

## 📖 Usage Guide

### 1. Basic Usage in Models

```python
from odoo import models, fields

class Invoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'jalaali.mixin']
    
    invoice_date_jalali = fields.Char(
        string="Invoice Date (Jalali)",
        compute='_compute_invoice_date_jalali',
        store=True
    )
    
    def _compute_invoice_date_jalali(self):
        for record in self:
            if record.invoice_date:
                record.invoice_date_jalali = self._gregorian_to_jalali(record.invoice_date)
            else:
                record.invoice_date_jalali = False
    
    @api.constrains('invoice_date_jalali')
    def _check_invoice_date(self):
        for record in self:
            if record.invoice_date_jalali:
                record._validate_jalali_date(record.invoice_date_jalali, 'Invoice Date')
```

### 2. Using in Forms (Automatic)

When user has "Use Jalali Calendar" enabled, all date fields automatically display in Jalali format:

```xml
<form>
    <sheet>
        <group>
            <field name="date"/>  <!-- Shows Jalali if user prefers -->
            <field name="invoice_date"/>
        </group>
    </sheet>
</form>
```

### 3. Custom OWL Component

```javascript
import { JalaaliField } from "@jalaali_pro/components/jalaali_field";

// In your template:
<JalaaliField 
    value="record.my_date" 
    onChange="(value) => this.onDateChange(value)"
    onError="(msg) => this.showError(msg)"
/>
```

### 4. Excel/CSV Import

**Step 1:** Prepare your CSV file:
```csv
name,date,amount
"Invoice 1",1403-01-15,1000000
"Invoice 2",1403-02-20,2500000
```

**Step 2:** Go to **Settings → Import Jalali Dates**

**Step 3:** 
- Select your file
- Choose target model (e.g., "Invoices")
- Specify date field name (e.g., "date")
- Click "Preview" to see conversions
- Click "Import" to process

The wizard will:
- Auto-detect Jalali vs Gregorian dates
- Validate all dates before import
- Show errors for invalid rows
- Convert Jalali → Gregorian for storage

---

## 🔧 Configuration

### User Preferences

Each user can configure their own Jalali settings:

1. Go to **Settings → Users → Your Profile**
2. Open **Preferences** tab
3. Configure:
   - **Use Jalali Calendar**: Display dates in Jalali format
   - **Show Holidays in Calendar**: Highlight Persian holidays
   - **Week Start Day**: Saturday (default) or Monday

### Holiday Management

Manage Persian holidays:

1. Go to **Settings → Localization → Holidays**
2. Create/Edit holidays:
   - Fixed dates (e.g., Nowruz: 1/1)
   - Lunar/Islamic dates (calculated dynamically)

---

## 🧪 Testing

### Run Tests

```bash
./odoo-bin --test-enable --test-tags /jalaali_pro
```

### Manual Testing Checklist

- [ ] Install module without errors
- [ ] Enable Jalali for a test user
- [ ] Create record with date field - verify Jalali display
- [ ] Enter Jalali date manually (1403-01-15) - verify conversion
- [ ] Enter Gregorian date (2024-03-20) - verify no conversion
- [ ] Import CSV with Jalali dates
- [ ] Export data - verify Gregorian format
- [ ] Check calendar view shows holidays
- [ ] Test with different users (some with Jalali enabled, some without)

---

## 📁 Module Structure

```
jalaali_pro/
├── __manifest__.py              # Module manifest
├── requirements.txt             # Python dependencies
├── models/
│   ├── __init__.py
│   ├── jalaali_mixin.py         # Server-side conversion logic
│   └── jalaali_holiday.py       # Holiday model
├── wizard/
│   ├── __init__.py
│   └── import_jalali_wizard.py  # CSV/Excel import wizard
├── static/
│   ├── lib/jalaali-js/
│   │   └── jalaali.js           # Client-side conversion library
│   └── src/
│       ├── js/services/
│       │   └── jalaali_service.esm.js  # OWL service
│       ├── js/components/
│       │   └── jalaali_field.esm.js    # Reusable component
│       ├── xml/
│       │   └── jalaali_field.xml       # Component template
│       └── css/
│           └── jalaali_styles.css      # Styling
├── views/
│   ├── user_views.xml           # User preferences extension
│   ├── jalaali_holiday_views.xml
│   └── wizard_views.xml         # Import wizard UI
├── data/
│   └── holiday_data.xml         # Default holidays
├── security/
│   └── ir.model.access.csv      # Access rights
└── tests/
    └── test_jalaali.py          # Unit tests
```

---

## 🔌 API Reference

### Server-Side (Python)

```python
# Get mixin
env['jalaali.mixin']

# Convert Jalali → Gregorian
gregorian_date = env['jalaali.mixin']._jalali_to_gregorian('1403-01-15')
# Returns: datetime.date(2024, 4, 5)

# Convert Gregorian → Jalali
jalali_str = env['jalaali.mixin']._gregorian_to_jalali(datetime.date(2024, 4, 5))
# Returns: '1403-01-17'

# Validate Jalali date
try:
    env['jalaali.mixin']._validate_jalali_date('1403-01-15', 'Test Date')
except ValidationError as e:
    print(e)
```

### Client-Side (JavaScript)

```javascript
// Get service
const jalaali = await this.env.services.jalaali;

// Convert Gregorian → Jalali
const jalaliStr = jalaali.toJalali(new Date(2024, 3, 5));
// Returns: '1403-01-17'

// Convert Jalali → Gregorian
const gregorianDate = jalaali.toGregorian('1403-01-17');
// Returns: Date object

// Validate
const isValid = jalaali.isValid('1403-01-15');
// Returns: true/false

// Check holiday
const isHoliday = jalaali.isHoliday('1403-01-01');
// Returns: true (Nowruz)
```

---

## 🐛 Troubleshooting

### Issue: "jalaali is not defined"

**Solution:** Ensure assets are loaded:
1. Clear browser cache (Ctrl+Shift+R)
2. Regenerate assets: **Settings → Technical → Database Structure → Clear Asset Cache**
3. Check browser console for load order issues

### Issue: Dates not converting on import

**Solution:** 
1. Verify date field name matches exactly
2. Check CSV encoding (must be UTF-8)
3. Ensure year is 4 digits (1403, not 1403)

### Issue: Holidays not showing in calendar

**Solution:**
1. Enable "Show Holidays" in user preferences
2. Verify holidays exist: **Settings → Localization → Holidays**
3. Check calendar view mode (month/week/day)

---

## 🎯 Best Practices

1. **Always store as Gregorian**: Keep database in Gregorian for compatibility
2. **Validate on server**: Never trust client-side validation alone
3. **Use mixin**: Inherit `jalaali.mixin` for consistent behavior
4. **Test imports**: Always preview before importing large files
5. **Document fields**: Clearly label Jalali fields in UI

---

## 📈 Performance Tips

- The `jalaali.js` library is lightweight (<10KB)
- Conversions are cached where possible
- Holiday checking uses indexed database queries
- Import wizard processes rows in batches

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

---

## 📄 License

LGPL-3.0 License

---

## 📞 Support

For issues or questions:
- GitHub Issues: [link]
- Email: support@yourcompany.com
- Documentation: https://yourcompany.com/jalaali-pro-docs

---

## 🔄 Changelog

### Version 19.0.1.0.0 (Initial Release)
- ✅ Server-side conversion with jdatetime
- ✅ Client-side OWL components
- ✅ Hybrid input (Jalali + Gregorian)
- ✅ CSV/Excel import wizard
- ✅ Holiday management
- ✅ Per-user preferences
- ✅ Comprehensive tests
- ✅ Full accessibility support
