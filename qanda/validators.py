"""
Prompting the users for, and validating, answers.

These provide a simple, consistent and robust way of formatting prompts for
gathering information from a commandline user and validating their answers.
Users are prompted with a question and optionally explanatory help text and
hints of possible answers.

A question is usually formatted as follows::

	helptext ... (multiple lines if need be) ... helptext
	question (hints) [default]:

Multiple choice questions are formatted as::

	helptext ... (multiple lines if need be) ... helptext
	1. choice
	2. choice
	...
	N. choice
	question (hints) [default]:

"""


### IMPORTS

import defs

__all__ = [
	
]


### CONSTANTS & DEFINES

SPACE_RE = re.compile ('\s+')

YESNO_SYNONYMS = {
	'yes': 'y',
	'no': 'n',
	'true': 'y',
	'false': 'n',
	'on': 'y',
	'off': 'n',
}


### IMPLEMENTATION ###

class BaseValidator (object):
	"""
	Converts and validates user input.
	
	Should throw an error if any problems.
	"""
	def __call__ (self, value):
		# NOTE: override in subclass
		value = self.convert(value)
		self.validate (value)
		return value
	
	def validate (self, value):
		# NOTE: override in subclass
		# probably a series of assertions
		pass
	
	def convert (self, value):
		# NOTE: override in subclass
		return value
		
		
class Clean (Converter):
	"""
	Normalize values by stripping flanking space and converting to lower case.
	
	Note that this does not explicitly throw errors.
	"""
	def __call__ (self, value):
		return value.strip().lower()
		
		
class Synonyms (Converter):
	"""
	Map values to other values.
	
	Note that this does not explicitly throw errors. If a value is un-mapped,
	it is simply returned.
	"""
	def __init__ (self, dict):
		self._syns = dict
		
	def __call__ (self, value):
		return self._syns.get (value, value)
		
		
class Vocab (Converter):
	"""
	Ensure values fall within a fixed set.
	"""
	def __init__ (self, args):
		self._allowed_values = args
		
	def __call__ (self, value):
		assert value in self._allowed_values, "I don't understand '%s'." % value
		return value


class Nonblank (Converter):
	def validate (self, value):
		assert 0 < len(value), "can't be a blank string"
		return value
	

class Range (Converter):
	"""
	Only allow values between certain inclusive bounds.
	"""
	def __init__ (self, min=None, max=None):
		self.min = min
		self.max = max
	
	def __call__ (self, value):
		if self.min is not None:
			assert self.min <= value, "'%s' is lower than '%s'" % (value, self.min)
		if self.max is not None:
			assert value <= self.max, "'%s' is higher than '%s'" % (value, self.max)
		
		

### END #######################################################################
