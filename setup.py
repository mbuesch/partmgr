#!/usr/bin/env python3

from partmgr.core.version import VERSION_STRING
from distutils.core import setup


setup(	name		= "partmgr",
	version		= VERSION_STRING,
	description	= "Part manager",
	license		= "GNU General Public License v2 or later",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/cms/hacking/...",
	packages	= [ "partmgr",
			    "partmgr/core",
			    "partmgr/pricefetch",
			    "partmgr/gui", ],
	scripts		= [ "partmgr-gui",
			    "partmgr-import-partdb", ],
	keywords	= [ ],
	classifiers	= [
	],
#	long_description = open("README.txt").read(),
)
