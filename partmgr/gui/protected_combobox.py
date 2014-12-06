# -*- coding: utf-8 -*-
#
# PartMgr GUI - Protected combo box
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


class ProtectedComboBox(AbstractProtectedWidget):
	currentIndexChanged = Signal(int)

	def __init__(self, parent=None):
		AbstractProtectedWidget.__init__(self, parent)

		self.combo = QComboBox(self)
		self.setEditWidget(self.combo)

		self.setProtected()

		self.combo.currentIndexChanged.connect(
			self.__currentIndexChanged)

	def addItem(self, name, data):
		self.combo.addItem(name, data)

	def itemData(self, index):
		return self.combo.itemData(index)

	def findData(self, data):
		for i in range(0, self.combo.count()):
			if self.itemData(i) == data:
				return i
		return -1

	def currentIndex(self):
		return self.combo.currentIndex()

	def setCurrentIndex(self, index):
		self.combo.setCurrentIndex(index)

	def __sync(self):
		self.setReadOnlyText(self.combo.currentText())

	def __currentIndexChanged(self, newIndex):
		self.__sync()
		self.currentIndexChanged.emit(newIndex)
