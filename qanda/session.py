"""
A round of prompting the users for, and validating, answers.

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
# TODO: add readline support for better editting?


### IMPORTS

import types

import defs

__all__ = [
	'Session',
	'prompt',
]


### CONSTANTS & DEFINES

### IMPLEMENTATION ###

class Session (object):
	# XXX: in future, this may include initialization of readline etc.
	
	## Questions:
	def string (self, question, converters=[], help=None, hints=None, default=None,
			strip_flanking_space=False):
		"""
		Ask for and return text from the user.
		
		The simplest public question function and the basis of many of the others,
		this is a thin wrapper around the core `_ask` method that 
		
		"""
		return self._ask (question,
			converters=[],
			help=help,
			hints=hints,
			default=default,
			strip_flanking_space=strip_flanking_space,
			multiline=False,
		)
	
	def text (self, question, converters=[], help=None, hints=None, default=None,
			strip_flanking_space=False):
		"""
		Ask for and return text from the user.
		
		The simplest public question function and the basis of many of the others,
		this is a thin wrapper around the core `_ask` method that 
		
		"""
		return self._ask (question,
			converters=[],
			help=help,
			hints=hints,
			default=default,
			strip_flanking_space=strip_flanking_space,
			multiline=True,
		)
	
	
	def string (question, converters=[], help=None, hints=None, default=None,
			strip_flanking_space=True, allow_blank=True):
		if allow_blank:
			extra_converters = []
		else:
			extra_converters = [Nonblank()]
		return ask (question, converters=extra_converters+converters, help=help,
			hints=hints, default=default, strip_flanking_space=True)
		
	def integer (question, converters=[], help=None, hints=None, default=None,
			allow_blank=True, min=None, max=None):
		
		HOW DO WE DO INTEGER OR NONE?
	
	
	def short_choice (question, choice_str, converters=[], help=None, default=None):
		"""
		Ask the user to make a choice using single letters.
		"""
		## Preconditions:
		choice_str = choice_str.strip().lower()
		assert choice_str, "need choices for question"
		if default:
			default = default.lower()
			assert (len(default) == 1), \
			"ask_short_choice uses only single letters, not '%s'" % default
		## Main:
		if default:
			hints = "%s, default %s" % (choice_str, default)
		else:
			hints = choice_str
		## Postconditions & return:
		return ask (question,
			converters= converters or [Vocab(list(choice_str))],
			help=help, hints=hints, default=default)
	
	
	def yesno (question, help=None, default=None):
		choice_str = 'yn'
		return short_choice (question, choice_str,
			converters=[
				lambda s: s.strip().lower(),
				Synonyms(YESNO_SYNONYMS),
				Vocab(list(choice_str)),
			],
			help=help,
			default=default,
		)
	
	# :Parameters:
	#    choices
	#        An array of Choices, or raw strings
	#
	# Users can select a value by typing in the value or selecting a number.
	#
	def ask_long_choice (question, choices, help=None, default=None):
		"""
		Ask the user to make a choice from a list
		
		:Parameters:
			
		"""
		## Preconditions:
		assert choices, "need choices for question"
		if default:
			default = default.lower()
		## Main:
		# build choices list
		synonyms = {}
		vocab = []
		menu = []
		for i, c in enumerate (choices):
			if isinstance (c, basestring):
				val = c
				desc = c
				syns = []
			elif instance_of (c, Choice):
				val = c.value
				desc = c.desc or value
				syns = c.syns
			else:
				assert false, "shouldn't get here"
			assert val not in vocab, "duplicate choice value '%s'" % val
			vocab.append (val)
			menu_index = str(i + 1)
			syns.append(menu_index)
			for s in syns:
				assert not synonyms.has_key(s), "duplicate choice synonym '%s'" % s
				synonyms[s] = val
			menu.append ("   %s. %s" % (menu_index, desc))
		help = '\n'.join([help]+ menu).strip()
	
		## Postconditions & return:
		return ask (question,
			converters=[
				Synonyms(synonyms),
				Vocab(vocab)
			],
			help=help,
			hints='1-%s' % len(choices),
			default=default
		)
	
	## Internals
	def _ask (self, question, converters=[], help=None, choices=[], hints=None,
		default=None, multiline=False, strip_flanking_space=True):
		"""
		Ask for and return an answer from the user.
		
		:Parameters:
			question
				The text of the question asked.
			converters
				An array of conversion and validation functions to be called in
				sucession with the results of the previous. If any throws an error,
				it will be caught and the question asked again.
			help
				Introductory text to be shown before the question.
			hints
				Short reminder text of possible answers.
			default
				The value the answer will be set to before processing if a blank
				answer (i.e. just hitting return) is entered.
			strip_flanking_space
				If true, flanking space will be stripped from the answer before it is
				processed.
			
		This is the underlying function for getting information from the user. It
		prints the help text (if any), any menu of choices, prints the question
		and hints and then waits for input from the user. All answers are fed from
		the converters. If conversion fails, the question is re-asked.
		
		The following sequence is used in processing user answers:
		
		1. The raw input is read
		2. If the options is set, flanking space is stripped
		3. If the input is an empty string and a default answer is given, the input
			is set to that value (i.e. the default answer must be a valid input
			value)
		4. The input is feed through each converter in turn, with the the result
			of one feeding into the next.
		5. If the conversion raises an error, the question is asked again
		6. Otherwise the processed answer is returned
		
		"""
		## Preconditions:
		assert (question), "'ask' requires a question"
		
		## Main:
		# show leadin
		if help:
			print self._clean_text (help)
		for c in choices:
			print "   %s" % c.lstrip()
		
		# build actual question line
		question_str = self._clean_text ("%s%s: " % (
			question, _format_hints_text (hints, default)))
		
		# ask question until you get a valid answer
		while True:
			print question_str,
			# TODO: patch for readline and multiline
			raw_answer = raw_input()
			if strip_flanking_space:
				raw_answer = raw_answer.strip()
			if default:
				raw_answer = raw_answer or default
			try:
				for conv in converters:
					raw_answer = conv.__call__ (raw_answer)
			except StandardError, err:
				print "A problem: %s. Try again ..." % err
			except:
				print "A problem: unknown error. Try again ..."
			else:
				return raw_answer
	
	def _clean_text (self, text):
		"""
		Trim, un-wrap and rewrap text to be presented to the user.
		"""
		# XXX: okay so we don't wrap it. Should we? And is there text we don't
		# want to wrap?
		return defs.SPACE_RE.sub (' ', text.strip())
		
	
	def _format_hints_text (self, hints=None, default=None):
		"""
		Consistently format hints and default values for inclusion in questions.
		
		The hints section of the questions is formatted as::
		
			(hint text) [default value text]
			
		If hints or the default value are not supplied (i.e. they are set to None)
		that section does not appear. If neither is supplied, an empty string is
		returned.
		
		Some heuristics are used in presentation. If the hints is a list (e.g. of
		possible choices), these are formatted as a comma delimited list. If the
		default value is a blank string, '' is given to make this explicit.
		
		Note this does not check if the default is a valid value.
		
		For example::
		
			>>> print _format_hints_text()
			
			>>> print _format_hints_text([1, 2, 3], 'foo')
			 (1,2,3) [foo]
			>>> print _format_hints_text('1-3', '')
			 (1-3) ['']
			>>> print _format_hints_text('an integer')
			 (an integer)
			 
		"""
		hints_str = ''
		if hints is not None:
			# if hints is an array, join the contents
			if type(hints) in [types.ListType, types.TupleType]:
				hints = ','.join (['%s' % x for x in hints])
			hints_str = ' (%s)' % hints
		if default is not None:
			# quote empty default strings for clarity
			if default is '':
				default = "''"
			hints_str += ' [%s]' % default
		## Postconditions % return:
		return hints_str









class Choice (object):
	def __init__ (self, value, description=None, synonyms=[]):
		self.value = value
		self.desc = description
		self.synonyms = synonyms

# An always available session 
prompt = Session()


		
## DEBUG & TEST ###

if __name__ == "__main__":
	import doctest
	doctest.testmod()


### END #######################################################################
