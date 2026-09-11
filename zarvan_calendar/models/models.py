# -*- coding: utf-8 -*-
from odoo import models, fields, api

# Import mixin logic
from . import __init__ as models_init
# The mixin is defined in __init__.py for simplicity in this structure, 
# but normally would be in a separate file. 
# Since Odoo loads all .py in models/, the class ZarvanMixin is already registered.
