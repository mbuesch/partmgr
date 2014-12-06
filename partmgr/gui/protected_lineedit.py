# -*- coding: utf-8 -*-
#
# PartMgr GUI - Protected line edit
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


class ProtectedLineEdit(AbstractProtectedWidget):
	textChanged = Signal(str)

	def __init__(self, parent=None):
		AbstractProtectedWidget.__init__(self, parent)

		self.lineEdit = QLineEdit(self)
		self.setEditWidget(self.lineEdit)

		self.setProtected()

		self.lineEdit.textChanged.connect(self.__textChanged)

	def setText(self, newText):
		self.lineEdit.setText(newText)

	def __sync(self):
		self.setReadOnlyText(self.lineEdit.text())

	def __textChanged(self, newText):
		self.__sync()
		self.textChanged.emit(newText)
