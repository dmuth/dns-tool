#!/usr/bin/env python3
#
# Documentation on this file: 
#
#	https://packaging.python.org/tutorials/distributing-packages/
#	and https://setuptools.readthedocs.io/en/latest/setuptools.html
#
#
# To test this out locally:
#
#	pip install -e .
#


from setuptools import setup, find_packages


setup(
	name = "dns-tool",
	version = "1.0.0",
	description = "A tool for testing out DNS servers",
	long_description = "This is just something I wrote for seeing what it was like to create DNS packets from scratch and parse the responses from scratch.  If you find it useful, great! If you think I'm crazy for doing this, great!",
	url = "https://github.com/dmuth/dns-tool/",
	author = "Douglas Muth",
	author_email = "doug.muth@gmail.com",

	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3",
	],

	#
	# Copy dns-tool to be in our path.
	#
	scripts = [ "dns-tool" ],

	packages = find_packages(exclude=["contrib", "docs", "tests*"]),

	install_requires = [ "humanize" ],

	python_requires = ">=3",

	py_modules = [],
	
	)

