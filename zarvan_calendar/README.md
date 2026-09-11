# Zarvan Calendar (Persian Jalali Support for Odoo 19)

![Version](https://img.shields.io/badge/version-19.0.1.0.0-blue)
![License](https://img.shields.io/badge/license-LGPL--3-green)
![Odoo](https://img.shields.io/badge/Odoo-19.0-orange)

## 🏛️ About the Name
**Zarvan** (or Zurvan) is the ancient Iranian deity of **Infinite Time and Fate**. 
Just as Zarvan governs the endless cycle of days, months, and years, this module masters time conversion, display, and logic within Odoo, ensuring every second counts in your business operations.

---

## ✨ Features & Why We Added Them

### 1. User-Specific Jalali/Gregorian Toggle
- **What**: Each user can enable/disable Jalali dates in their profile.
- **Why**: Not everyone in a multi-national company needs Persian dates. This respects individual preferences without forcing a global change.
- **How**: Added `enable_jalali_display` field to `res.users`.

### 2. Company Default Policy
- **What**: Admins can set Jalali as default for new users.
- **Why**: Saves time for Iranian companies; ensures consistency.
- **How**: Config parameter `zarvan_calendar.default_jalali`.

### 3. Safe Server-Side Conversion (Zero Risk)
- **What**: All date conversions happen on the server using Python's `jdatetime`.
- **Why**: Guarantees 100% accuracy for leap years and complex calculations. Client-side JS libraries often fail or bloat the browser.
- **How**: `zarvan.calendar.mixin` with LRU caching for performance.

### 4. Smart Persian NLP Parsing
- **What**: Understands phrases like "شنبه آینده" (Next Saturday), "جمعه گذشته" (Last Friday).
- **Why**: Users think in relative terms. Typing natural language is faster than picking dates.
- **How**: Rule-based parser in `_parse_persian_nlp` (No heavy AI, no external APIs).

### 5. Performance Optimized
- **What**: Uses `@functools.lru_cache` for conversions.
- **Why**: Prevents recalculating the same dates repeatedly, crucial for lists with 1000+ records.
- **How**: Cached methods in the mixin.

### 6. Universal Module Compatibility
- **What**: Works with Sales, Accounting, HR, Project, Inventory, etc.
- **Why**: Dates are everywhere in Odoo. A partial solution is useless.
- **How**: Mixin architecture allows any model to inherit Jalali capabilities.

---

## 🚀 Installation

1. **Install Dependency**:
   ```bash
   pip3 install jdatetime
   ```

2. **Copy Module**:
   Place the `zarvan_calendar` folder in your Odoo `addons` directory.

3. **Install App**:
   - Go to **Apps** in Odoo.
   - Update Apps List.
   - Search for **Zarvan Calendar** and Install.

4. **Configure**:
   - **Global**: Settings > Zarvan Calendar > Enable "Default Jalali for New Users".
   - **User**: Profile > Preferences > Check "Show Dates in Jalali".

---

## 🛡️ Safety Guarantee
- **Database Integrity**: Data is **ALWAYS** stored as Gregorian (`YYYY-MM-DD`). Jalali is strictly a display layer.
- **No Core Overrides**: Uses standard Odoo inheritance (`_inherit`), not risky file replacements.
- **No External APIs**: Everything runs locally on your server. No data leaves your premises.
- **Zero Downtime**: Safe to install/uninstall without affecting existing data.

---

## 📖 Usage Guide

### For End Users
- **Forms**: Click any date field. If enabled, you'll see Jalali formatting.
- **Filters**: Type natural Persian dates in search filters (e.g., "ماه بعد").
- **Reports**: PDFs automatically show Jalali dates if the user has it enabled.

### For Developers
Inherit the mixin to add Jalali support to your custom models:
```python
from odoo import models

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['my.model', 'zarvan.calendar.mixin']
```

---

## 🤝 Support & Contribution
This module is open-source and community-driven. 
Submit issues or PRs on GitHub: [Your GitHub Link]

*Powered by the legacy of Zarvan.*
