{
    "name": "Jalaali Core Utilities",
    "version": "19.0.1.0.0",
    "category": "Localization/Iran",
    "summary": "Core Persian Calendar Logic & Auto-Conversion",
    "description": """
        Provides robust Jalali/Gregorian conversion utilities for Odoo 19.
        
        Features:
        - High-performance JDate class (OWL compatible)
        - Server-side auto-conversion for Date/Datetime fields
        - CSV/Excel import support (auto-detects Jalali format)
        - Configuration for per-user/per-company activation
    """,
    "author": "Odoo Community",
    "website": "https://github.com/odoo-community",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
        "views/res_company_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "jalaali_core/static/src/lib/jalaali.js",
            "jalaali_core/static/src/owl_components/**/*.js",
            "jalaali_core/static/src/xml/**/*.xml"
        ]
    },
    "installable": True,
    "auto_install": False,
}
