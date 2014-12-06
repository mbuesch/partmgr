# -*- coding: utf-8 -*-
#
# PartMgr GUI - Protected spin box
#
# Copyright 2014 Michael Buesch <m@bues.ch>
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

from partmgr.gui.protected_widget import *
from partmgr.gui.util import *


class ProtectedSpinBox(AbstractProtectedWidget):
	valueChanged = Signal(int)

	def __init__(self, parent=None):
		AbstractProtectedWidget.__init__(self, parent)

		self.spin = QSpinBox(self)
		self.spin.setAccelerated(True)
		self.setKeyboardTracking(True)
		self.setEditWidget(self.spin)

		self.__sync()
		self.setProtected()

		self.spin.valueChanged.connect(self.__valueChanged)

	def setKeyboardTracking(self, on=True):
		self.spin.setKeyboardTracking(on)

	def setMinimum(self, value):
		self.spin.setMinimum(value)

	def setMaximum(self, value):
		self.spin.setMaximum(value)

	def setSingleStep(self, value):
		self.spin.setSingleStep(value)

	def setSuffix(self, suffix):
		self.spin.setSuffix(suffix)
		self.__sync()

	def setValue(self, value):
		self.spin.setValue(value)

	def __sync(self):
		self.setReadOnlyText("%d%s" % (self.spin.value(),
					       self.spin.suffix()))

	def __valueChanged(self, newValue):
		self.__sync()
		self.valueChanged.emit(newValue)
