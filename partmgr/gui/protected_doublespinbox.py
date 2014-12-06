# -*- coding: utf-8 -*-
#
# PartMgr GUI - Protected double spin box
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


class ProtectedDoubleSpinBox(AbstractProtectedWidget):
	valueChanged = Signal(float)

	class _DoubleSpinBox(QDoubleSpinBox):
		def textFromValue(self, value):
			text = self.parent().textFromValue(value)
			if text is None:
				return QDoubleSpinBox.textFromValue(self, value)
			return text

		def valueFromText(self, text):
			value = self.parent().valueFromText(text)
			if value is None:
				return QDoubleSpinBox.valueFromText(self, text)
			return value

	def __init__(self, parent=None):
		AbstractProtectedWidget.__init__(self, parent)

		self.spin = self._DoubleSpinBox(self)
		self.spin.setAccelerated(True)
		self.setKeyboardTracking(True)
		self.setEditWidget(self.spin)

		self.__sync()
		self.setProtected()

		self.spin.valueChanged.connect(self.__valueChanged)

	def textFromValue(self, value):
		return None

	def valueFromText(self, text):
		return None

	def setKeyboardTracking(self, on=True):
		self.spin.setKeyboardTracking(on)

	def setMinimum(self, value):
		self.spin.setMinimum(value)

	def setMaximum(self, value):
		self.spin.setMaximum(value)

	def setDecimals(self, value):
		self.spin.setDecimals(value)

	def setSingleStep(self, value):
		self.spin.setSingleStep(value)

	def setSuffix(self, suffix):
		self.spin.setSuffix(suffix)
		self.__sync()

	def setValue(self, value):
		self.spin.setValue(value)

	def __sync(self):
		self.setReadOnlyText(self.spin.cleanText() +\
				     self.spin.suffix())

	def __valueChanged(self, newValue):
		self.__sync()
		self.valueChanged.emit(newValue)
