# -*- encoding: utf-8 -*-
# This file is distributed under the same license as the Django package.
#
from __future__ import unicode_literals

# The *_FORMAT strings use the Django date format syntax,
# see http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'j בF Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'j בF Y, H:i'
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'j בF'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'
# FIRST_DAY_OF_WEEK = 

# The *_INPUT_FORMATS strings use the Python strftime format syntax,
# see http://docs.python.org/library/datetime.html#strftime-strptime-behavior
# DATE_INPUT_FORMATS = 
# TIME_INPUT_FORMATS = 
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%dT%H:%M',     
    '%Y-%m-%dT%H:%M:%S',  
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%d/%m/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%d/%m/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%d/%m/%Y %H:%M',        # '10/25/2006 14:30'
    '%d/%m/%Y',              # '10/25/2006'
    '%d/%m/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%d/%m/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%d/%m/%y %H:%M',        # '10/25/06 14:30'
    '%d/%m/%y',              # '10/25/06'
) 
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','
# NUMBER_GROUPING = 
