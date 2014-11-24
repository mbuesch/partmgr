# -*- coding: utf-8 -*-
#
# PartMgr GUI - Abstract protected widget
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

from partmgr.gui.util import *


class AbstractProtectedWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QVBoxLayout(self))

		self.label = QLabel(self)
		self.label.setFrameShape(QFrame.Panel)
		self.label.setFrameShadow(QFrame.Sunken)
		font = self.label.font()
		font.setBold(True)
		self.label.setFont(font)
		self.layout().addWidget(self.label)

		self.editWidgets = []

		self.setProtected()

	def addEditWidget(self, widget):
		self.layout().addWidget(widget)
		self.editWidgets.append(widget)

	def setProtected(self, prot=True):
		if prot:
			for widget in self.editWidgets:
				widget.hide()
			self.label.show()
			margins = QMargins(5, 0, 5, 0)
		else:
			for widget in self.editWidgets:
				widget.show()
			self.label.hide()
			margins = QMargins()
		self.layout().setContentsMargins(margins)

	def clear(self):
		self.label.clear()
		for widget in self.editWidgets:
			widget.clear()

	def setReadOnlyText(self, text):
		self.label.setText(text)
