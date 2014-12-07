# -*- coding: utf-8 -*-
#
# PartMgr GUI - Group select widget
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


class GroupSelectWidget(QWidget):
	"Abstract multiple items selection widget"

	def __init__(self, parent=None, newButtonLabel="New"):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(QMargins())

		self.selectWidgets = []
		self.payloadLayout = QVBoxLayout()
		self.payloadLayout.setContentsMargins(QMargins())
		self.layout().addLayout(self.payloadLayout, 0, 0)

		if newButtonLabel:
			l = QHBoxLayout()
			l.addStretch()
			self.newButton = QPushButton(newButtonLabel, self)
			self.newButton.released.connect(self.createNewGroup)
			l.addWidget(self.newButton)
			self.layout().addLayout(l, 1, 0)

		self.setProtected()
		self.clear()

	def setProtected(self, prot=True):
		self.protected = prot
		for selWidget in self.selectWidgets:
			selWidget.setProtected(prot)
		try:
			self.newButton.setEnabled(not prot)
		except AttributeError as e:
			pass

	def clear(self):
		for w in self.selectWidgets:
			w.deleteLater()
		self.selectWidgets = []

	def addItemSelectWidget(self, itemSel):
		self.payloadLayout.addWidget(itemSel)
		self.selectWidgets.append(itemSel)

	def finishUpdate(self):
		self.setProtected(self.protected)

	def createNewGroup(self):
		raise NotImplementedError
