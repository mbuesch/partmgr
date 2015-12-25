# -*- coding: utf-8 -*-
#
# QT bindings wrapper
#
# Copyright 2015 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys
import os


def __frameworkError(msg):
	print("partmgr-gui ERROR: " + msg)
	input("Press enter to exit.")
	sys.exit(1)

def __testQStringAPI(scope, silent=False):
	# Test for QString v2 API
	if "QString" in scope:
		# QString exists. This is v1 API.
		if silent:
			return False
		__frameworkError("Deprecated QString API detected.\n"
				 "partmgr does not support PyQt QString v1 API.\n"
				 "---> Please use PySide or a newer PyQt with v2 APIs. <---")
	return True

def __autodetectGuiFramework():
	urls = {
		"pyside" : "http://www.pyside.org/",
		"pyqt4" : "http://www.riverbankcomputing.com/software/pyqt/download",
		"pyqt5" : "http://www.riverbankcomputing.com/software/pyqt/download5",
	}
	try:
		import PyQt5.QtCore as __pyQtCore
		if __testQStringAPI(dir(__pyQtCore), True):
			return "pyqt5"
	except ImportError:
		pass
	try:
		import PySide.QtCore as __pySideCore
		return "pyside4"
	except ImportError:
		pass
	try:
		import PyQt4.QtCore as __pyQtCore
		if __testQStringAPI(dir(__pyQtCore), True):
			return "pyqt4"
	except ImportError:
		pass
	__frameworkError("Neither PySide nor PyQt found.\n"
			 "PLEASE INSTALL PySide (%s)\n"
			 "            or PyQt4 with v2 APIs (%s)\n"
			 "            or PyQt5 with v2 APIs (%s)" %\
			 (urls["pyside"],
			  urls["pyqt4"],
			  urls["pyqt5"]))

# The Qt bindings can be set via PARTMGRGUI environment variable.
__guiFramework = os.getenv("PARTMGRGUI", "auto").lower()

# Run Qt autodetection
if __guiFramework == "auto":
	__guiFramework = __autodetectGuiFramework()
if __guiFramework == "pyside":
	__guiFramework = "pyside4"
if __guiFramework == "pyqt":
	__guiFramework = "pyqt5"

# Load the Qt modules
if __guiFramework == "pyside4":
	print("partmgr-gui: Using PySide4 GUI framework")
	try:
		from PySide.QtCore import *
		from PySide.QtGui import *
	except ImportError as e:
		__frameworkError("Failed to import PySide modules:\n" + str(e))
elif __guiFramework == "pyqt4":
	print("partmgr-gui: Using PyQt4 GUI framework")
	try:
		from PyQt4.QtCore import *
		from PyQt4.QtGui import *
	except ImportError as e:
		__frameworkError("Failed to import PyQt4 modules:\n" + str(e))
	__testQStringAPI(globals())
	# Compatibility
	Signal = pyqtSignal
elif __guiFramework == "pyqt5":
	print("partmgr-gui: Using PyQt5 GUI framework")
	try:
		from PyQt5.QtCore import *
		from PyQt5.QtGui import *
		from PyQt5.QtWidgets import *
	except ImportError as e:
		__frameworkError("Failed to import PyQt5 modules:\n" + str(e))
	__testQStringAPI(globals())
	# Compatibility
	Signal = pyqtSignal
else:
	__frameworkError("Unknown GUI framework '%s' requested. "
			 "Please fix PARTMGRGUI environment variable." %\
			 __guiFramework)

# Helpers for distinction between Qt4 and Qt5 API.
isQt4 = (__guiFramework == "pyside4" or\
	 __guiFramework == "pyqt4")
isQt5 = (__guiFramework == "pyqt5")

# Helpers for distinction between PySide and PyQt API.
isPySide = __guiFramework.startswith("pyside")
isPyQt = __guiFramework.startswith("pyqt")
