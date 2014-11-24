#!/usr/bin/env python3

from distutils.core import setup


setup(	name		= "partmgr",
	version		= "0.0",
	description	= "Part manager",
	license		= "GNU General Public License v2 or later",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/cms/hacking/...",
	packages	= [ "partmgr",
			    "partmgr/core",
			    "partmgr/gui", ],
	scripts		= [ "partmgr-gui", ],
	keywords	= [ ],
	classifiers	= [
	],
#	long_description = open("README.txt").read(),
)
