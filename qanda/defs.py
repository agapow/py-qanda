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

try:
	import colorama as clr
	COLORAMA_AVAILABLE = True
	DEFAULT_STYLES = {
		'HELP':       clr.Style.DIM,
		'CHOICES':    clr.Fore.BLUE,
		'QUESTION':   clr.Fore.CYAN,
		'HINTS':      clr.Fore.BLUE,
		'ANSWER':     clr.Fore.WHITE,
		'ERROR':      clr.Fore.RED,
	}
except:
	COLORAMA_AVAILABLE = False
	DEFAULT_STYLES = {}



### END #######################################################################
