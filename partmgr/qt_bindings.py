# -*- coding: utf-8 -*-
#
# QT bindings wrapper
#
# Copyright 2015-2022 Michael Buesch <m@bues.ch>
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

def __autodetectGuiFramework():
	urls = {
		"pyside6" : "https://wiki.qt.io/Qt_for_Python",
		"pyqt6" : "https://riverbankcomputing.com/software/pyqt/download",
	}
	try:
		import PyQt6.QtCore as __pyQtCore
		return "pyqt6"
	except ImportError:
		pass
	try:
		import PySide6.QtCore as __pySideCore
		return "pyside6"
	except ImportError:
		pass
	__frameworkError("Neither PySide nor PyQt found.\n"
			 "PLEASE INSTALL PySide6 (%s)\n"
			 "            or PyQt6 (%s)" %\
			 (urls["pyside6"],
			  urls["pyqt6"]))

# The Qt bindings can be set via PARTMGRGUI environment variable.
__guiFramework = os.getenv("PARTMGRGUI", "auto").lower()

# Run Qt autodetection
if __guiFramework == "auto":
	__guiFramework = __autodetectGuiFramework()
if __guiFramework == "pyside":
	__guiFramework = "pyside6"
if __guiFramework == "pyqt":
	__guiFramework = "pyqt6"

# Load the Qt modules
if __guiFramework == "pyside6":
	print("partmgr-gui: Using PySide6 GUI framework")
	try:
		from PySide6.QtCore import *
		from PySide6.QtGui import *
		from PySide6.QtWidgets import *
	except ImportError as e:
		__frameworkError("Failed to import PySide6 modules:\n" + str(e))
elif __guiFramework == "pyqt6":
	print("partmgr-gui: Using PyQt6 GUI framework")
	try:
		from PyQt6.QtCore import *
		from PyQt6.QtGui import *
		from PyQt6.QtWidgets import *
	except ImportError as e:
		__frameworkError("Failed to import PyQt6 modules:\n" + str(e))
	# Compatibility
	Signal = pyqtSignal
else:
	__frameworkError("Unknown GUI framework '%s' requested. "
			 "Please fix PARTMGRGUI environment variable." %\
			 __guiFramework)

# Helpers for distinction between PySide and PyQt API.
isPySide = __guiFramework.startswith("pyside")
isPyQt = __guiFramework.startswith("pyqt")
