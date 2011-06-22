===========
About qanda
===========

Background
----------

Interactive command-line programs need to query users for information, be it
text, choices from a list, or simple yes-or-no answers. *qanda* is a Python
module of simple functions to prompt users for such information, with validation
and cleanup of answers, allowing default responses, consistent formatting and
presentation of help text, hints and choices. It is not a replacement for
textual interfaces like curses and urwid, but intended solely for simple console
scripts.


Installation
------------

The simplest way to install *qanda* is via ``easy_install`` or an equivalent
program::

	% easy_install qanda

Alternatively the tarball can be downloaded, unpacked and ``setup.py`` run::

	% tar zxvf qanda.tgz
	% cd qanda
	% python set.py install

*qanda* has no requisites and should work with just about any version of Python.


Using qanda
-----------

Examples
~~~~~~~~

::

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
	>>> years = prompt.integer ("And what is your age", min=1, max=100)
	And what is your age: 101
	A problem: 101 is higher than 100. Try again ...
	And what is your age: 28



Central concepts
~~~~~~~~~~~~~~~~

*qanda* packages all question-asking methods in a Session class. This allows
the appearance and functioning of all these methods to be handled consistently
and modified centrally. However, you don't necessarily have to create a Session
to use it - there's pre-existing Session in the variable called ``prompt``::

	>>> from qanda import Session
	>>> s = Session()
	>>> from qanda import prompt
	>>> type (prompt)
	<class 'qanda.session.Session'>

The question methods are named after the type of data they elicit::

	>>> print type(prompt.integer ("Pick a number"))
	Pick a number: 2
	<type 'int'>
	>>> print type(prompt.string ("Pick a name"))
	Pick a name: Bob
	<type 'string'>

Many of the question methods with accept a list of "converters", each of which
is used to sucessively transform or validate user input. If input fails
validation, the question is posed again. *qanda* supplies a number of basic
validators::


References
----------
