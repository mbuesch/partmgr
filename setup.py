#!/usr/bin/env python3

from partmgr.core.version import VERSION_STRING
from distutils.core import setup
import sys
try:
	import py2exe
except ImportError as e:
	py2exe = None
try:
	if py2exe and "py2exe" in sys.argv:
		raise ImportError
	from cx_Freeze import setup, Executable
	cx_Freeze = True
except ImportError as e:
	cx_Freeze = False


freezeExecutables = [ ("partmgr-gui", None), ]
extraKeywords = {}
if py2exe:
	extraKeywords["console"] = [ s for s, e in freezeExecutables ]
if cx_Freeze:
	executables = []
	for script, exe in freezeExecutables:
		if exe:
			if os.name.lower() in ("nt", "ce"):
				exe += ".exe"
			executables.append(Executable(script = script,
						      targetName = exe))
		else:
			executables.append(Executable(script = script))
	extraKeywords["executables"] = executables
	extraKeywords["options"] = {
			"build_exe"     : {
				"packages"      : [ "partmgr", ],
			}
		}

setup(	name		= "partmgr",
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
	scripts		= [ "partmgr-gui",
			    "partmgr-import-partdb", ],
	keywords	= [ ],
	classifiers	= [
	],
#	long_description = open("README.txt").read(),
	**extraKeywords
)
