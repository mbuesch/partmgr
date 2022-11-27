# -*- coding: utf-8 -*-
#
# PartMgr GUI - Abstract entity manage dialog
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

from partmgr.core.parameter import *


class UserParamWidget(QWidget):
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

class AbstractEntityManageDialog(QDialog):
	"Abstract Entity manage dialog"

	# Flags
	HIDE_DELBUTTON		= 1 << 0
	HIDE_NEWBUTTON		= 1 << 1
	READONLY_DESC		= 1 << 2
	READONLY_NAME		= 1 << 3
	NO_PARAMETERS		= 1 << 4

	class ListItem(QListWidgetItem):
		def __init__(self, entity):
			QListWidgetItem.__init__(self, entity.getName())
			self.setData(Qt.ItemDataRole.UserRole, entity)

		def getEntity(self):
			return self.data(Qt.ItemDataRole.UserRole)

	def __init__(self, db, title,
		     entitySpecificWidget=None, parent=None,
		     entFlags=0):
		QDialog.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.setWindowTitle(title)

		self.db = db
		self.entFlags = entFlags
		self.updateBlocked = 0

		self.titleLabel = QLabel(title, self)
		self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
		font = self.titleLabel.font()
		font.setPointSize(12)
		self.titleLabel.setFont(font)
		self.layout().addWidget(self.titleLabel, 0, 0, 1, 3)

		self.entityList = QListWidget(self)
		self.layout().addWidget(self.entityList, 1, 0, 4, 1)

		rightLayout = QGridLayout()
		y = 0

		self.nameLabel = QLabel("Name:")
		rightLayout.addWidget(self.nameLabel, y, 0)
		self.nameEdit = QLineEdit(self)
		rightLayout.addWidget(self.nameEdit, y, 1)
		y += 1
		if entFlags & self.READONLY_NAME:
			self.nameEdit.setEnabled(False)

		self.descLabel = QLabel("Description:")
		rightLayout.addWidget(self.descLabel, y, 0)
		self.descEdit = QLineEdit(self)
		rightLayout.addWidget(self.descEdit, y, 1)
		y += 1
		self.descEdit.textChanged.connect(self.descChanged)
		if entFlags & self.READONLY_DESC:
			self.descEdit.setEnabled(False)

		if entFlags & self.NO_PARAMETERS == 0:
			self.userParamLayout = QVBoxLayout()
			self.userParamWidgets = []
			rightLayout.addLayout(self.userParamLayout, y, 0, 1, 2)
			y += 1

			self.newUserParamButton = QPushButton("New parameter")
			rightLayout.addWidget(self.newUserParamButton, y, 1)
			y += 1

		if entitySpecificWidget:
			rightLayout.addWidget(entitySpecificWidget,
					      y, 0, 1, 2)
			y += 1

		rightLayout.setRowStretch(y, 1)
		y += 1

		self.layout().addLayout(rightLayout, 1, 1, 5, 1)

		buttonsLayout = QHBoxLayout()
		if entFlags & self.HIDE_NEWBUTTON == 0:
			self.newButton = QPushButton("Create &new")
			buttonsLayout.addWidget(self.newButton)
			self.newButton.released.connect(self.newEntity)
		if entFlags & self.HIDE_DELBUTTON == 0:
			self.delButton = QPushButton("&Delete")
			buttonsLayout.addWidget(self.delButton)
			self.delButton.released.connect(self.delEntity)
		self.layout().addLayout(buttonsLayout, 5, 0)

		self.closeButton = QPushButton("&Close window")
		self.layout().addWidget(self.closeButton, 6, 0, 1, 3)

		# Pin the title height
		self.titleLabel.setFixedHeight(
			self.titleLabel.size().height())

		self.entSelChanged()

		self.entityList.currentItemChanged.connect(
						self.entSelChanged)
		self.nameEdit.textChanged.connect(self.nameChanged)
		self.closeButton.released.connect(self.accept)
		if entFlags & self.NO_PARAMETERS == 0:
			self.newUserParamButton.released.connect(self.__newUserParam)

	def __newUserParam(self):
		curItem = self.entityList.currentItem()
		if not curItem:
			return
		param = Parameter("<unnamed>",
				  data = "<enter data here>")
		curItem.getEntity().addParameter(param)
		self.entSelChanged(curItem, curItem)

	def __delUserParam(self, paramWidget):
		paramWidget.param.delete()
		curItem = self.entityList.currentItem()
		self.entSelChanged(curItem, curItem)

	def updateData(self, entities=[], selectEntity=None):
		self.entityList.clear()
		entities.sort(key=lambda ent: ent.getName())
		selectItem = None
		for entity in entities:
			item = self.ListItem(entity)
			self.entityList.addItem(item)
			if selectEntity and selectEntity == entity:
				selectItem = item
		if selectItem:
			self.entityList.setCurrentItem(selectItem)

	def edit(self, selectEntity=None):
		self.updateData(selectEntity)
		return self.exec()

	def entSelChanged(self, item=None, prevItem=None):
		self.updateBlocked += 1

		if item:
			entity = item.getEntity()
			self.nameEdit.setText(entity.getName())
			self.descEdit.setText(entity.getDescription())
		else:
			self.nameEdit.clear()
			self.descEdit.clear()
		if self.entFlags & self.READONLY_NAME == 0:
			self.nameEdit.setEnabled(bool(item))
		if self.entFlags & self.READONLY_DESC == 0:
			self.descEdit.setEnabled(bool(item))
		if self.entFlags & self.HIDE_DELBUTTON == 0:
			self.delButton.setEnabled(bool(item))
		if self.entFlags & self.NO_PARAMETERS == 0:
			while self.userParamWidgets:
				widget = self.userParamWidgets.pop(0)
				self.userParamLayout.removeWidget(widget)
				widget.deleteLater()
			if item:
				params = item.getEntity().getAllParameters()
				for param in params:
					paramWidget = UserParamWidget(param)
					paramWidget.remove.connect(self.__delUserParam)
					self.userParamWidgets.append(paramWidget)
					self.userParamLayout.addWidget(paramWidget)

		self.updateBlocked -= 1

	def nameChanged(self, newName):
		if self.updateBlocked:
			return
		curItem = self.entityList.currentItem()
		if not curItem:
			return
		entity = curItem.getEntity()
		entity.setName(newName)
		curItem.setText(newName)

	def descChanged(self, newDesc):
		if self.updateBlocked:
			return
		curItem = self.entityList.currentItem()
		if not curItem:
			return
		entity = curItem.getEntity()
		entity.setDescription(newDesc)

	def delEntity(self):
		curItem = self.entityList.currentItem()
		if not curItem:
			return
		entity = curItem.getEntity()
		ret = QMessageBox.question(self,
			"Really delete %s?" % entity.getEntityType().lower(),
			"Really delete %s '%s'?" % (
				entity.getEntityType().lower(),
				entity.getName()),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if ret & QMessageBox.StandardButton.Yes == 0:
			return
		entity.delete()
		self.updateData()

	def newEntity(self):
		raise NotImplementedError
