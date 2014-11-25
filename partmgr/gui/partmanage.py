# -*- coding: utf-8 -*-
#
# PartMgr GUI - Part manage dialog
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

from partmgr.gui.entitymanage import *
from partmgr.gui.util import *

from partmgr.core.part import *


class PartEditWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(QMargins())

		self.layout().setColumnStretch(0, 1)
		self.layout().setColumnStretch(2, 2)

		self.name0 = QLineEdit(self)
		self.layout().addWidget(self.name0, 0, 0)
		self.label0 = QLabel(":", self)
		self.layout().addWidget(self.label0, 0, 1)
		self.text0 = QLineEdit(self)
		self.layout().addWidget(self.text0, 0, 2)

		self.name1 = QLineEdit(self)
		self.layout().addWidget(self.name1, 1, 0)
		self.label1 = QLabel(":", self)
		self.layout().addWidget(self.label1, 1, 1)
		self.text1 = QLineEdit(self)
		self.layout().addWidget(self.text1, 1, 2)

		self.name2 = QLineEdit(self)
		self.layout().addWidget(self.name2, 2, 0)
		self.label2 = QLabel(":", self)
		self.layout().addWidget(self.label2, 2, 1)
		self.text2 = QLineEdit(self)
		self.layout().addWidget(self.text2, 2, 2)

		self.currentPart = None
		self.changeBlocked = 0

		self.name0.textChanged.connect(self.__textChanged)
		self.text0.textChanged.connect(self.__textChanged)
		self.name1.textChanged.connect(self.__textChanged)
		self.text1.textChanged.connect(self.__textChanged)
		self.name2.textChanged.connect(self.__textChanged)
		self.text2.textChanged.connect(self.__textChanged)

	def updateData(self, part):
		self.changeBlocked += 1

		self.currentPart = part

		self.name0.setEnabled(bool(part))
		self.name0.clear()
		self.text0.setEnabled(bool(part))
		self.text0.clear()
		self.name1.setEnabled(bool(part))
		self.name1.clear()
		self.text1.setEnabled(bool(part))
		self.text1.clear()
		self.name2.setEnabled(bool(part))
		self.name2.clear()
		self.text2.setEnabled(bool(part))
		self.text2.clear()

		if part:
			pass#TODO
#			self.name0.setText(part.getText0()[0])
#			self.text0.setText(part.getText0()[1])
#			self.name1.setText(part.getText1()[0])
#			self.text1.setText(part.getText1()[1])
#			self.name2.setText(part.getText2()[0])
#			self.text2.setText(part.getText2()[1])

		self.changeBlocked -= 1

	def __textChanged(self, unused):
		if self.changeBlocked:
			return
		if not self.currentPart:
			return
#TODO		self.currentPart.setText0(self.name0.text(), self.text0.text())
#		self.currentPart.setText1(self.name1.text(), self.text1.text())
#		self.currentPart.setText2(self.name2.text(), self.text2.text())

class PartManageDialog(AbstractEntityManageDialog):
	"Part create/modify/delete dialog"

	def __init__(self, stockItem, parent=None):
		self.stockItem = stockItem
		self.editWidget = PartEditWidget()
		AbstractEntityManageDialog.__init__(self, stockItem.db,
			"Manage parts", self.editWidget, parent)

		self.nameLabel.setText("Part name:")

	def updateData(self, selectPart=None):
		AbstractEntityManageDialog.updateData(
			self, self.stockItem.getAllParts(),
			selectPart)

	def entSelChanged(self, item=None, prevItem=None):
		AbstractEntityManageDialog.entSelChanged(self,
			item, prevItem)
		part = item.getEntity() if item else None
		self.editWidget.updateData(part)

	def newEntity(self):
		newPart = Part("Unnamed", "", self.stockItem.category,
			       db=self.stockItem.db)
		self.db.modifyPart(newPart)
		self.updateData(newPart)
