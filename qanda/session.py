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

import konval
from konval.impl import make_list

import defs

__all__ = [
	'Session',
	'prompt',
]


### CONSTANTS & DEFINES

### IMPLEMENTATION ###

class Session (object):
	"""
	Encapsulated methods for interacting the a use via a text UI.
	
	This "holds" all the different Q-and-A methods, allowing them to be formatted
	consistently and customized to together. 
	"""
	# XXX: in future, this may include initialization of readline etc.

	def __init__ (self, use_styles=True, styles={}):
		self.choice_delim = '/'
		self.use_styles = use_styles and defs.COLORAMA_AVAILABLE
		self.styles = dict (defs.DEFAULT_STYLES)
		self.styles.update (styles)

	## Questions:
	def string (self, question, converters=[], help=None, hints=None,
			default=None, default_value=None,
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
			default_value=default_value,
			strip_flanking_space=strip_flanking_space,
			multiline=False,
		)

	def text (self, question, converters=[],
			help=None, hints=None,
			default=None, default_value=None,
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
			default_value=default_value,
			strip_flanking_space=strip_flanking_space,
			multiline=True,
		)

	def integer (self, question, converters=[], help=None, hints=None,
			default=None, default_value=None, min=None, max=None):
		return self.string (question,
			converters=[konval.ToInt(), konval.Range (min, max)] + converters,
			help=help,
			hints=hints,
			default=default,
			default_value=default_value,
			strip_flanking_space=True,
		)


	def short_choice (self, question, choice_str, converters=[], help=None,
			default=None, default_value=None, err_msg=None):
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
		err_msg = err_msg or "choice must be from '%s'" % choice_str
		## Postconditions & return:
		return self._ask (question,
			converters = converters or [konval.IsInVocab(list(choice_str))],
			help=help, hints=hints,
			default=default, default_value=default_value,
			err_msg=err_msg,
		)


	def yesno (self, question, help=None, default=None, default_value=None):
		choice_str = 'yn'
		return self.short_choice (question, choice_str,
			converters=[konval.StrToBool()],
			help=help,
			default=default,
			default_value=default_value,
			err_msg="choice must be yes or no",
		)

	def long_choice (self, question, choices, help=None, default=None,
			default_value=None):
		"""
		Ask the user to make a choice from a list.

		A choice is a list of strings and/or pairs of strings. If a pair is
		provided, the first is the visible string, the second the actual returned
		value. If only a string is provided, it is used for both.
		"""
		## Preconditions:
		assert choices, "need choices for question"
		if default:
			default = default.lower()
		## Main:
		# build choices list
		choices = [make_list(x) for x in choices]
		syns = {}
		vocab = []
		menu = []
		for i, c in enumerate (choices):
			menu_index = str(i + 1)
			syns[menu_index] = c[-1]
			menu.append ("%s. %s" % (menu_index, c[0]))
		
		## Postconditions & return:
		return self._ask (question,
			converters=[
				konval.IsInVocab ([str(x+1) for x in range(len(choices))]),
				konval.ToSynonym (syns),
			],
			help=help,
			choices = menu,
			hints='1-%s' % len(choices),
			default=default,
			default_value=default_value,
			err_msg="choice must be from 1-%s" % len(choices),
		)

	## Internals
	def _ask (self, question, converters=[],
			choices=[],
			help=None, hints=None,
			default=None, default_value=None, 
			multiline=False,
			strip_flanking_space=True,
			err_msg=None,
		):
		"""
		Ask for and return an answer from the user.

		:Parameters:
			question
				The text of the question asked.
			converters
				An array of conversion and validation functions to be called in
				succession with the results of the previous. If any throws an error,
				it will be caught and the question asked again.
			help
				Introductory text to be shown before the question.
			hints
				Short reminder text of possible answers.
			default
				The value the answer will be set to before processing if a blank
				answer (i.e. just hitting return) is entered.
			default_value
				The value that will be returned immediately if a blank
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
			
			3. If the input is an empty string:
		
				1. if default_value is set, that value is returned immediately
				   (i.e. bypass conversion and validation)
				
				2. if default is set, the input is set to that value (i.e.
				   the default will be processed and thus validate)
				
			4. The input is feed through each converter in turn, with the the result
				of one feeding into the next.
				
			5. If the conversion raises an error, the question is asked again
			
			6. Otherwise the processed answer is returned
			
		Note the two ways of returning a default value. Note that it is also
		impossible to set the default or default value to None as this is used
		to test whether they have been set.

		"""
		## Preconditions:
		assert (question), "'ask' requires a question"

		## Main:
		# show leadin
		if help:
			print "%s%s%s" % (
				self.set_style ('HELP'),
				self._clean_text (help), 
				self.reset_style()
			)
		for c in choices:
			print "   %s%s%s" % (
				self.set_style ('CHOICES'), 
				c.lstrip(),
				self.reset_style()
			)
			
		# build actual question line
		question_str = self._clean_text (
			"%(q_style)s%(q)s%(reset)s%(hint)s%(q_style)s:%(reset)s" % {
				'q':         question, 
				'q_style':   self.set_style('QUESTION'),
				'hint':      self._format_hints_text (hints, default, default_value),
				'reset':     self.reset_style(),
			}
		)
		
		err_msg = err_msg or "%(err)s"
		
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
			if (raw_answer == ''):
				if (default_value is not None):
					# return default value immediately
					return default_value
				if (default is not None):
					# send default for processing
					raw_answer = default
			try:
				for conv in converters:
					raw_answer = conv.__call__ (raw_answer)
			except StandardError, err:
				message = err_msg % {
					'err': err,
					'bad_val': raw_answer,
				}
				print "%sA problem: %s. Try again ...%s" % (self.set_style('ERROR'),
					message, self.reset_style())
			except:
				print "%sA problem: unknown error. Try again ...%s" % (
					self.set_style('ERROR'), self.reset_style())
			else:
				return raw_answer

	def _clean_text (self, text):
		"""
		Trim, un-wrap and rewrap text to be presented to the user.
		"""
		# XXX: okay so we don't wrap it. Should we? And is there text we don't
		# want to wrap?
		return defs.SPACE_RE.sub (' ', text.strip())


	def _format_hints_text (self, hints=None, default=None, default_value=None):
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
		# what default gets printed? the value then the plain
		if default_value is None:
			default_print = default
		else:
			default_print = default_value
		# quote empty default strings for clarity
		if default_print is not None:
			if default is '':
				default = "''"
			hints_str += ' %s[%s]%s' % (
				self.set_style('HINTS'), 
				default, 
				self.reset_style()
			)
		## Postconditions % return:
		return hints_str
	
	def set_style (self, style):
		"""
		Return the necessary symbols to set styles and color.
		"""
		if self.use_styles:
			return self.styles[style]
		else:
			return ''
		
	def reset_style (self):
		"""
		Return the necessary symbols to set style back to default.
		"""
		if self.use_styles:
			return defs.clr.Style.RESET_ALL
		else:
			return ''
		
		

	def read_input_line (self, prompt):
		"""
		Read and return a single line of user input.

		Input is terminated by return or enter (which is stripped).
		"""
		# raw_input uses readline if available
		return raw_input(prompt + ' ')

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
		line_arr = [self.read_input_line (prompt + ' ')]
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
