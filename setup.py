from setuptools import setup, find_packages
import sys, os

import qanda

setup (
	name=qanda.__name__,
	version=qanda.__version__,
	description="Simple text prompts and validation for user input",
	long_description="""\
	Interactive command-line programs need to query users for information, be it text, choices from a list, or simple yes-no answers. qanda is a library of simpel functions to prompt users for such information, with validate and cleanup of answers, allowing default answers, concistent formatting and presentatioon of hepl text and choices. It is not a replacement for textual interfaces like curses and urwid, but intended solely for commandline scripts.""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='text commandline ui prompt',
	author=qanda.__author__,
	author_email=qanda.__email__,
	url='http://www.agapow.net/software/py-qanda',
	license='MIT',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		 # -*- Extra requirements: -*-
	],
	entry_points="""
	# -*- Entry points: -*-
	""",
)
