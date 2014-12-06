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


class PartUserParamWidget(QWidget):
	remove = Signal(QWidget)

	def __init__(self, param, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(QMargins())

		self.param = param

		self.layout().setColumnStretch(0, 1)
		self.layout().setColumnStretch(2, 2)

		self.name = QLineEdit(self)
		self.layout().addWidget(self.name, 0, 0)
		label = QLabel(":", self)
		self.layout().addWidget(label, 0, 1)
		self.text = QLineEdit(self)
		self.layout().addWidget(self.text, 0, 2)
		self.delButton = QPushButton("Remove", self)
		self.layout().addWidget(self.delButton, 0, 3)

		self.name.setText(self.param.getName())
		self.text.setText(self.param.getDataString())

		self.name.textChanged.connect(self.__handleNameChange)
		self.text.textChanged.connect(self.__handleTextChange)
		self.delButton.released.connect(self.__handleDel)

	def __handleDel(self):
		self.remove.emit(self)

	def __handleNameChange(self, newName):
		self.param.setName(newName)

	def __handleTextChange(self, newText):
		self.param.setData(newText)

class PartEditWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout())
		self.layout().setContentsMargins(QMargins())

		self.layout().setColumnStretch(0, 2)
		self.layout().setColumnStretch(1, 1)

		self.userParamLayout = QVBoxLayout()
		self.userParamWidgets = []
		self.layout().addLayout(self.userParamLayout, 0, 0, 1, 2)

		self.newUserParamButton = QPushButton("New parameter")
		self.layout().addWidget(self.newUserParamButton, 1, 1)

		self.currentPart = None
		self.changeBlocked = 0

		self.newUserParamButton.released.connect(self.__newUserParam)

	def __newUserParam(self):
		if not self.currentPart:
			return
		param = Parameter("<unnamed>",
				  data = "<enter data here>")
		self.currentPart.addParameter(param)
		self.updateData(self.currentPart)

	def __delUserParam(self, paramWidget):
		paramWidget.param.delete()
		self.updateData(self.currentPart)

	def updateData(self, part):
		self.changeBlocked += 1

		self.currentPart = part

		while self.userParamWidgets:
			widget = self.userParamWidgets.pop(0)
			self.userParamLayout.removeWidget(widget)
			widget.deleteLater()

		if part:
			params = part.getAllParameters()
			for param in params:
				paramWidget = PartUserParamWidget(param)
				paramWidget.remove.connect(self.__delUserParam)
				self.userParamWidgets.append(paramWidget)
				self.userParamLayout.addWidget(paramWidget)

		self.changeBlocked -= 1

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
		newPart = Part("Unnamed",
			       category = self.stockItem.category,
			       db = self.stockItem.db)
		self.db.modifyPart(newPart)
		self.updateData(newPart)
