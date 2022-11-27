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
		self.layout().setContentsMargins(QMargins())

		self.label = QLabel(self)
		self.label.setFrameShape(QFrame.Shape.Panel)
		self.label.setFrameShadow(QFrame.Shadow.Sunken)
		font = self.label.font()
		font.setBold(True)
		self.label.setFont(font)
		self.layout().addWidget(self.label)

		self.editWidget = None

		self.setProtected()

	def minimumSizeHint(self):
		size = QWidget.minimumSizeHint(self)
		if self.editWidget:
			edSize = self.editWidget.minimumSizeHint()
			size.setWidth(max(size.width(), edSize.width()))
			size.setHeight(max(size.height(), edSize.height()))
		return size

	def sizeHint(self):
		size = QWidget.sizeHint(self)
		if self.editWidget:
			edSize = self.editWidget.sizeHint()
			size.setWidth(max(size.width(), edSize.width()))
			size.setHeight(max(size.height(), edSize.height()))
		return size

	def setEditWidget(self, widget):
		widget.hide()
		if self.editWidget:
			self.layout().removeWidget(self.editWidget)
		self.layout().addWidget(widget)
		self.editWidget = widget
		self.setProtected()

	def setProtected(self, prot=True):
		if prot:
			if self.editWidget:
				self.editWidget.hide()
			self.label.show()
		else:
			if self.editWidget:
				self.editWidget.show()
			self.label.hide()

	def clear(self):
		self.label.clear()
		if self.editWidget:
			self.editWidget.clear()

	def setReadOnlyText(self, text):
		self.label.setText(text)
