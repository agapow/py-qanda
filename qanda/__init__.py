"""
Simple text prompts and validation for user input.

Interactive command-line programs need to query users for information, be it
text, choices from a list, or simple yes-no answers. *qanda* is a library of
simple functions to prompt users for such information, with validation and
cleanup of answers, allowing default answers, consistent formatting and
presentation.

For example::

	>>> from qanda import prompt
	>>> prompt.string ("What is your name")
	What is your name: Foo
	>>> fname = prompt.string ("Your friends name is",
			help="I need to know your friends name as well before I talk to you.",
			hints="first name",
			default='Bar',
		)
	I need to know your friends name as well before I talk to you.
	Your friends name is (first name) [Bar]:
	>>> print fname
	Bar
	>>> 
	
	
"""

__version__ = "0.1"
__author__ = "Paul-Michael Agapow"
__email__ = "pma@agapow.net"


### IMPORTS

from session import *


### CONSTANTS & DEFINES

### IMPLEMENTATION ###

### END #######################################################################

