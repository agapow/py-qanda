"""
Various module-wide constants.
"""

### IMPORTS

import re

__all__ = [
	'SPACE_RE',
	'YESNO_SYNONYMS',
]


### CONSTANTS & DEFINES

SPACE_RE = re.compile ('\s+')

ANSWER_YES = 'y'
ANSWER_NO = 'n'

YESNO_SYNONYMS = {
	'yes': 'y',
	'no': 'n',
	'true': 'y',
	'false': 'n',
	'on': 'y',
	'off': 'n',
}


### END #######################################################################
