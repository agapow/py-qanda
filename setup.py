from setuptools import setup, find_packages
import sys, os

import qanda

setup (
	name=qanda.__name__,
	version=qanda.__version__,
	description="Simple text prompts and validation for user input",
	long_description=open("README.txt").read() + "\n" +
		open(os.path.join("docs", "HISTORY.txt")).read(),
	classifiers=[
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Topic :: Software Development :: User Interfaces',
	],
	keywords='text commandline ui prompt',
	author=qanda.__author__,
	author_email=qanda.__email__,
	url='http://www.agapow.net/software/py-qanda',
	license='MIT',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	include_package_data=True,
	exclude_package_data={
		'': ['tests'],
	},
	zip_safe=False,
	install_requires=[
		 # -*- Extra requirements: -*-
	],
	entry_points="""
		# -*- Entry points: -*-
	""",
	test_suite='nose.collector',
)
