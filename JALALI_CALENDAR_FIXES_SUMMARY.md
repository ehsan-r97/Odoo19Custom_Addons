# Jalali Calendar Module Fixes - Summary Report

## Overview
This document summarizes the critical fixes applied to the Odoo 19 Jalali/Persian calendar modules (`burna_persian_calendar` and `burna_calendar`).

---

## 🔧 Fixes Applied to `burna_persian_calendar`

### 1. Asset Loading Order Problem (CRITICAL)
**Issue:** Separate bundles caused `farvardin` object to be undefined when needed by other scripts.

**Fix:** 
- Merged all assets into a single `web.assets_backend` bundle
- Enforced strict loading order in `__manifest__.py`:
  1. `utils.js` (JDate class definition)
  2. `farvardin.js` (conversion library)
  3. Format utilities and view patches
  4. Date picker components
  5. Loader service

**File Modified:** `__manifest__.py`

```python
'assets': {
    'web.assets_backend': [
        # Load order is critical - farvardin must be loaded first
        'burna_persian_calendar/static/lib/jalali/utils.js',
        'burna_persian_calendar/static/src/js/farvardin.js',
        'burna_persian_calendar/static/src/js/format_utils.js',
        # ... rest of files in dependency order
    ],
}
```

### 2. Missing Server-Side Validation (CRITICAL)
**Issue:** 100% client-side dependency meant API calls, CSV imports, and XML-RPC operations bypassed all validation.

**Fix:** Created new server-side validation mixin:
- **File:** `models/persian_validation.py`
- Abstract model `persian.calendar.validation` with methods:
  - `_validate_jalali_date()` - Validates Jalali date strings
  - `_is_jalali_leap_year()` - Leap year detection
  - `_jalali_to_gregorian()` - Server-side conversion
- Proper range checking (year: 1300-1500, month: 1-12, day: 1-31)
- Month-specific day validation (30 vs 31 days)
- Esfand leap year handling

### 3. No Unit Tests (CRITICAL)
**Issue:** Critical date conversion logic had zero test coverage.

**Fix:** Created comprehensive test suite:
- **File:** `tests/test_persian_validation.py`
- Tests for:
  - Valid Jalali dates (including edge cases)
  - Invalid Jalali dates (wrong format, out-of-range values)
  - Leap year detection accuracy
  - Jalali-to-Gregorian conversion correctness

### 4. Redundant Libraries Issue
**Issue:** Three different Jalali conversion implementations existed (`utils.js`, `farvardin.js`, `persian-date.js`).

**Fix:** 
- Removed reference to unused `persian-date.js` from manifest
- Consolidated to use only `utils.js` (JDate class) and `farvardin.js`

---

## 🔧 Fixes Applied to `burna_calendar`

### 1. Performance Problem - DOM Mutation Observer (CRITICAL)
**Issue:** Observer watched entire document tree (`subtree: true` on `document.body`), causing severe performance degradation.

**Fix:** Limited observer scope:
- First attempts to observe only calendar containers (`.o_calendar_view`, `.fc`, `.o_calendar_container`)
- Falls back to body observation with `subtree: false` if containers not found
- Added null-check for addedNodes before processing

**File Modified:** `static/src/js/shamsi_calendar.js`

```javascript
// Limit observer scope to calendar containers only
const calendarContainers = document.querySelectorAll(CALENDAR_ROOT_SELECTORS.join(","));

if (calendarContainers.length > 0) {
    calendarContainers.forEach((container) => {
        observer.observe(container, { /* options */ });
    });
} else {
    // Fallback with subtree: false for performance
    observer.observe(document.body, {
        childList: true,
        subtree: false, // KEY FIX
        attributes: true,
        attributeFilter: ["data-date", "value"],
    });
}
```

### 2. Input Logic Flaw - Date Corruption (CRITICAL)
**Issue:** Focus/blur conversion could corrupt partially typed dates because conversion happened on every blur regardless of whether value changed.

**Fix:** 
- Store original value on focus: `input._originalValue = input.value`
- Only convert back to Gregorian if value actually changed
- Cleanup temporary storage on blur

**File Modified:** `static/src/js/shamsi_calendar.js`

```javascript
input.addEventListener("focus", () => {
    input._originalValue = input.value;
    convertInputToShamsi(input);
});

input.addEventListener("change", () => {
    if (input._originalValue !== input.value) {
        convertInputToGregorian(input);
    }
});
```

### 3. Weak Validation - Accepts Invalid Dates (HIGH)
**Issue:** Regex accepted invalid dates like `9999-99-99`.

**Fix:** Enhanced validation in `jalali_utils.js`:
- Added range validation for Jalali dates (year: 1300-1500)
- Added range validation for Gregorian dates (year: 1900-2100)
- Month validation (1-12)
- Day validation (1-31)

**File Modified:** `static/src/js/jalali_utils.js`

```javascript
export function isJalaliDateString(value) {
    const trimmed = (value || "").trim();
    if (!/^\d{4}[-/]\d{1,2}[-/]\d{1,2}$/.test(trimmed)) {
        return false;
    }
    const [y, m, d] = normalized.split("-").map((x) => parseInt(x, 10));
    // Validate ranges
    if (y < 1300 || y > 1500 || m < 1 || m > 12 || d < 1 || d > 31) {
        return false;
    }
    return true;
}
```

---

## 📋 Remaining Issues (Not Fixed)

### Shared Issues Requiring Future Work:

1. **Hardcoded Locale (`fa_IR`)**
   - Both modules only support `fa_IR` locale
   - Should support `fa_AF`, `ps`, and other Persian variants
   - **Recommendation:** Make locale configurable via system parameters

2. **Missing Accessibility Features**
   - No ARIA labels on calendar widgets
   - Keyboard navigation incomplete
   - Screen reader support missing
   - **Recommendation:** Add ARIA attributes and test with screen readers

3. **Incomplete DateTimePicker (burna_persian_calendar)**
   - Only patches navigation logic
   - Time selection may not work correctly with Jalali dates
   - Validation hooks missing
   - **Recommendation:** Full rewrite of datetime picker component

4. **Limited Scope of burna_calendar**
   - Only works in Calendar view
   - Does not support forms, lists, or kanbans
   - **Recommendation:** Consider merging with burna_persian_calendar

5. **No Documentation**
   - No README files
   - No usage examples
   - No configuration guide
   - **Recommendation:** Create comprehensive documentation

---

## ✅ Verification Checklist

After applying these fixes, verify:

- [ ] Assets load in correct order (check browser console for errors)
- [ ] Jalali date picker appears in form views
- [ ] Calendar view displays Jalali dates correctly
- [ ] CSV import validates Jalali dates server-side
- [ ] API calls with invalid Jalali dates are rejected
- [ ] No performance issues in calendar view (check DevTools)
- [ ] Partial date entry doesn't corrupt values
- [ ] Invalid dates like `9999-99-99` are rejected
- [ ] Unit tests pass: `odoo-bin -i burna_persian_calendar --test-enable`

---

## 📁 Files Modified/Created

### burna_persian_calendar
| File | Action | Purpose |
|------|--------|---------|
| `__manifest__.py` | Modified | Fixed asset loading order |
| `models/__init__.py` | Created | Model initialization |
| `models/persian_validation.py` | Created | Server-side validation |
| `tests/__init__.py` | Created | Test initialization |
| `tests/test_persian_validation.py` | Created | Unit tests |

### burna_calendar
| File | Action | Purpose |
|------|--------|---------|
| `static/src/js/shamsi_calendar.js` | Modified | Performance + input logic fixes |
| `static/src/js/jalali_utils.js` | Modified | Enhanced validation |

---

## 🚀 Installation Instructions

1. Update module list in Odoo Apps
2. Install `burna_persian_calendar` (includes all fixes)
3. Install `burna_calendar` (for enhanced calendar view)
4. Set user language to Persian (Iran) / `fa_IR`
5. Restart Odoo server to clear asset cache
6. Run tests: `./odoo-bin -i burna_persian_calendar --test-enable`

---

## ⚠️ Important Notes

- **Database remains Gregorian:** All dates are stored as Gregorian in the database
- **UI displays Jalali:** Conversion happens only in the UI layer
- **API compatibility:** Existing APIs continue to work with Gregorian dates
- **Backward compatible:** No breaking changes to existing functionality

