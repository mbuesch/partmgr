#!/usr/bin/env python3

from setuptools import setup
import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, basedir)

from partmgr.core.version import VERSION_STRING

if os.name.lower() == "nt":
	from cx_Freeze import setup, Executable
	cx_Freeze = True
else:
	cx_Freeze = False

extraKeywords = {}
if cx_Freeze:
	extraKeywords["executables"] = [
		Executable(script="partmgr-gui"),
	]
	extraKeywords["options"] = {
		"build_exe" : {
			"packages" : [ "partmgr", ],
		}
	}

with open(os.path.join(basedir, "README.rst"), "rb") as fd:
	readmeText = fd.read().decode("UTF-8")

setup(
	name		= "partmgr",
	version		= VERSION_STRING,
	description	= "Part manager",
	license		= "GNU General Public License v2 or later",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/h/partmgr",
	packages	= [ "partmgr",
			    "partmgr/core",
			    "partmgr/pricefetch",
			    "partmgr/gui", ],
	scripts		= [ "partmgr-gui", ],
	keywords	= [ ],
	install_requires = [ "PySide6", ],
	classifiers	= [
	],
	long_description=readmeText,
	long_description_content_type="text/x-rst",
	**extraKeywords
)
