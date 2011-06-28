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

__docformat__ = "restructuredtext en"


### IMPORTS

import types

import defs
import validators

__all__ = [
	'Session',
	'prompt',
]


### CONSTANTS & DEFINES

### IMPLEMENTATION ###

class Session (object):
	# XXX: in future, this may include initialization of readline etc.
	
	def __init__ (self):
		self.choice_delim = '/'
	
	## Questions:
	def string (self, question, converters=[], help=None, hints=None,
			default=None, convert_default=True, 
			strip_flanking_space=False):
		"""
		Ask for and return text from the user.
		
		The simplest public question function and the basis of many of the others,
		this is a thin wrapper around the core `_ask` method that 
		
		"""
		return self._ask (question,
			converters=converters,
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
		this is a thin wrapper around the core `_ask` method that allows for
		multi-line responses.
		
		"""
		return self._ask (question,
			converters=[],
			help=help,
			hints=hints,
			default=default,
			strip_flanking_space=strip_flanking_space,
			multiline=True,
		)
		
	def integer (self, question, converters=[], help=None, hints=None,
			default=None, convert_default=True, min=None, max=None):
		return self.string (question,
			converters=[validators.ToInt(), validators.Range (min, max)] + converters,
			help=help,
			hints=hints,
			default=default,
			convert_default=convert_default,
			strip_flanking_space=True,
		)
	
	
	def short_choice (self, question, choice_str, converters=[], help=None, default=None):
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
		hints = choice_str
		## Postconditions & return:
		return self._ask (question,
			converters= converters or [validators.Vocab(list(choice_str))],
			help=help, hints=hints, default=default)
	
	
	def yesno (self, question, help=None, default=None):
		choice_str = 'yn'
		return self.short_choice (question, choice_str,
			converters=[
				lambda s: s.strip().lower(),
				validators.Synonyms(YESNO_SYNONYMS),
				Vocab(list(choice_str)),
			],
			help=help,
			default=default,
		)
	
	def ask_long_choice (self, question, choices, help=None, default=None):
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
		return self._ask (question,
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
		default=None, convert_default=True, multiline=False,
		strip_flanking_space=True):
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
			convert_default
				If the default value is used, it will be processed through the
				converters. Otherwise it will be dircetly returned.
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
			3. If the input is an empty string and a default answer is given:
			
				1. if convert_default is set, the input is set to that value (i.e.
				the default answer must be a valid input value)
				
				2. else return default value immediately (bypass conversion)
				
			4. The input is feed through each converter in turn, with the the result
				of one feeding into the next.
			5. If the conversion raises an error, the question is asked again
			6. Otherwise the processed answer is returned
		
		"""
		# XXX: the convert_default and default handling is a little tricksy:
		# - you can't return a default value of None (without some fancy
		#   converting), because None is intepreted as no default
		# - It makes sense to process/convert the default value, as this ensures
		#   that the default value is valid (converts correctly) and the printed
		#   value can be different to the returned value.
		# - However this makes some queries difficult, like "ask for an integer
		#   or return False", where the default value is of a different type. Thus
		#   the (occasional) need for `convert_default=False`.
		
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
			question, self._format_hints_text (hints, default)))
		
		# ask question until you get a valid answer
		while True:
			if multiline:
				raw_answer = self.read_input_multiline (question_str)
			else:
				raw_answer = self.read_input_line (question_str)
			if strip_flanking_space:
				raw_answer = raw_answer.strip()
			# if the answer is blank and a default has been supplied
			# NOTE: makes it impossible to have a default value of None
			if (raw_answer == '') and (default is not None):
				if convert_default:
					# feed default through converters
					raw_answer = default
				else:
					# return default value immmediately
					return default
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
		
			>>> print prompt._format_hints_text()
			<BLANKLINE>
			>>> print prompt._format_hints_text([1, 2, 3], 'foo')
			 (1,2,3) [foo]
			>>> print prompt._format_hints_text('1-3', '')
			 (1-3) ['']
			>>> print prompt._format_hints_text('an integer')
			 (an integer)
			 
		"""
		hints_str = ''
		if hints is not None:
			# if hints is an array, join the contents
			if type(hints) in [types.ListType, types.TupleType]:
				hints = self.choice_delim.join (['%s' % x for x in hints])
			hints_str = ' (%s)' % hints
		if default is not None:
			# quote empty default strings for clarity
			if default is '':
				default = "''"
			hints_str += ' [%s]' % default
		## Postconditions % return:
		return hints_str

	def read_input_line (self, prompt):
		"""
		Read and return a single line of user input.
		
		Input is terminated by return or enter (which is stripped).
		"""
		# raw_input uses readline if available
		return raw_input(prompt)
		
	def read_input_multiline (self, prompt):
		"""
		Read and return multiple lines of user input.
		
		Input is terminated by two blank lines. Input is returned as a multiline
		string, with newlines at the linebreaks.
		"""
		# TODO: be nice to make end condition flexible.
		# NOTE: because raw_input can use readline, the readline up-arrow can
		# "paste-in" multiple lines of text in one go. So a bit of post-parsing
		# is required.
		# NOTE: we don't even attempt to cope with anything but unix yet
		line_arr = [self.read_input_line (prompt)]
		if line_arr[0] == '':
			line_arr = []
		else:
			while True:
				line_arr.append(self.read_input_line ('... '))
				if line_arr[-2:] == ['', '']:
					line_arr = line_arr[:-2]
					break
		clean_arr = []
		for line in line_arr:
			clean_arr.extend (line.split('\n'))
		return '\n'.join (clean_arr)


# An always available session 
prompt = Session()



## DEBUG & TEST ###

if __name__ == "__main__":
	import doctest
	doctest.testmod()


### END #######################################################################
