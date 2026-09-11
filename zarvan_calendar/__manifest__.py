# -*- coding: utf-8 -*-
{
    'name': 'Zarvan Calendar',
    'version': '19.0.1.0.0',
    'category': 'Localization/Iran',
    'summary': 'Complete Persian (Jalali) Calendar Support for Odoo 19',
    'description': """
Zarvan Calendar - Persian Date Integration for Odoo 19
======================================================
Named after Zurvan, the ancient Iranian deity of Infinite Time.

Features:
---------
* User-specific Jalali/Gregorian date toggle
* Native Jalali Date Picker in forms and filters
* Smart Persian NLP date parsing (e.g., "شنبه آینده")
* Automatic Jalali display in Reports, Emails, Activities
* Fiscal Year support based on Persian calendar
* Performance optimized with server-side caching
* Zero risk: Database remains pure Gregorian

Safe, Stable, Production-Ready.
    """,
    'author': 'Your Name',
    'website': 'https://github.com/yourusername/zarvan_calendar',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/res_users.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zarvan_calendar/static/src/js/**/*.js',
            'zarvan_calendar/static/src/components/**/*.js',
            'zarvan_calendar/static/src/components/**/*.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
