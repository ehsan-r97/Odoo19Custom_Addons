{
    "name": "Professional Jalali Calendar (Jalaali Pro)",
    "version": "19.0.1.0.0",
    "summary": "Complete Jalali/Persian calendar support with server-side conversion, OWL widgets, and Excel import.",
    "description": """
        Professional Jalali Calendar Solution for Odoo 19
        
        Features:
        - Automatic Jalali <-> Gregorian conversion (Server & Client)
        - Smart Hybrid Input (accepts both formats)
        - OWL Reusable Components
        - CSV/Excel Import Wizard with validation
        - Per-user calendar preferences
        - Holiday & Weekend visualization
        - Comprehensive test suite
        - Full accessibility support (ARIA, keyboard nav)
        
        Storage remains Gregorian for compatibility with reports, exports, and integrations.
    """,
    "author": "Your Company",
    "website": "https://www.yourcompany.com",
    "category": "Localization/Persian",
    "depends": ["base", "web", "calendar"],
    "data": [
        "security/ir.model.access.csv",
        "views/jalaali_holiday_views.xml",
        "views/user_views.xml",
        "views/wizard_views.xml",
        "data/holiday_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "jalaali_pro/static/lib/jalaali-js/jalaali.js",
            "jalaali_pro/static/src/js/services/jalaali_service.esm.js",
            "jalaali_pro/static/src/js/components/jalaali_field.esm.js",
            "jalaali_pro/static/src/js/components/jalaali_calendar_renderer.esm.js",
            "jalaali_pro/static/src/css/jalaali_styles.css",
        ],
        "web.assets_tests": [
            "jalaali_pro/static/src/tests/jalaali_tests.esm.js",
        ],
    },
    "external_dependencies": {
        "python": ["jdatetime"],
    },
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
