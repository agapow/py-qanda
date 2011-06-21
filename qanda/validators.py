"""
Prompting the users for, and validating, answers.

In *qanda*, answers from a user may be processed through a list of validators.
This follows the idiom of Ian Bicking & FormEncode where validation and
conversion are one and the same: raw values are passed into a converter and the
results are passed into the next. Should an exception be raised, conversion is
halted and 

"""
# TODO: "or" validator


### IMPORTS

import re
import exceptions

import defs

__all__ = [
	
]


### CONSTANTS & DEFINES

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


class Clean (BaseValidator):
	"""
	Normalize values by stripping flanking space and converting to lower case.
	
	Note that this does not explicitly throw errors.
	"""
	def __call__ (self, value):
		return value.strip().lower()


class Synonyms (BaseValidator):
	"""
	Map values to other values.
	
	Note that this does not explicitly throw errors. If a value is un-mapped,
	it is simply returned.
	"""
	def __init__ (self, dict):
		self._syns = dict
		
	def __call__ (self, value):
		return self._syns.get (value, value)


class Vocab (BaseValidator):
	"""
	Ensure values fall within a fixed set.
	"""
	def __init__ (self, args):
		self._allowed_values = args
		
	def __call__ (self, value):
		assert value in self._allowed_values, "I don't understand '%s'" % value
		return value


class Nonblank (BaseValidator):
	"""
	Only allow values non-blank strings (i.e. those with a length more than 0).
	"""
	def validate (self, value):
		assert 0 < len(value), "can't be a blank string"
		return value


class Regex (BaseValidator):
	"""
	Only allow values that match a certain pattern.
	"""
	def __init__ (self, patt):
		self.re = re.compile (patt)
	
	def __call__ (self, value):
		assert self.re.match (value)
		return value


class Range (BaseValidator):
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
		return value


class ToInt (BaseValidator):
	def validate (self, value):
		try:
			conv_val = int (value)
			return conv_val
		except:
			raise exceptions.ValueError ("not an integer")


class ToFloat (BaseValidator):
	def validate (self, value):
		try:
			conv_val = float (value)
			return conv_val
		except:
			raise exceptions.ValueError ("not a float")



### END #######################################################################
