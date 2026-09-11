# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Persian Calendar",
    'summary': """Jalali/Persian Calendar Support for Forms, Lists, and Kanban Views""",
    'description': """
        Persian Calendar Module for Odoo 19
        ====================================
        This module adds full Jalali (Persian/Shamsi) calendar support to Odoo forms,
        list views, kanban views, and date pickers.
        
        Features:
        - Jalali date picker widget with full calendar navigation
        - Automatic conversion between Gregorian (storage) and Jalali (display)
        - Server-side validation for API and CSV imports
        - Support for fa_IR locale
        - Leap year detection and validation
        
        Usage:
        Install the module and set user language to Persian (Iran) to enable Jalali dates.
    """,
    'author': "Odoo Community Iran",
    'website': "https://odoo-community.ir/",
    'category': 'Localization/Iran',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            # Consolidated bundle - JDate utils loaded first
            'burna_persian_calendar/static/lib/jalali/utils.js',
            # Core conversion library (removed redundant farvardin.js dependency)
            'burna_persian_calendar/static/src/js/format_utils.js',
            # View renderers
            'burna_persian_calendar/static/src/js/list.js',
            'burna_persian_calendar/static/src/js/kanban.js',
            # Date/time field patches
            'burna_persian_calendar/static/src/js/datepicker/datetime_field.js',
            'burna_persian_calendar/static/src/js/datepicker/datetime_picker.js',
            # Service layer with improved conversion logic
            'burna_persian_calendar/static/src/js/datepicker/datetimepicker_service.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'external_dependencies': {
        'python': [],
    },
}
