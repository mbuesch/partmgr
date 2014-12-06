# -*- coding: utf-8 -*-
#
# PartMgr GUI - Parameter manage dialog
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

from partmgr.core.parameter import *


class ParameterEditWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(QMargins())

		self.layout().addWidget(QLabel("Parameter value:"))

		self.combo = QComboBox(self)
		self.layout().addWidget(self.combo)
		self.combo.currentIndexChanged.connect(self.__comboChanged)

		self.currentParam = None
		self.changeBlocked = 0
		self.updateData()

	def updateData(self, param=None):
		self.changeBlocked += 1

		self.combo.clear()
		self.combo.hide()

		self.currentParam = param
		if not param:
			pass
		elif param.getName() == "currency":
			currencies = list(Param_Currency.CURRNAMES.keys())
			currencies.sort(key = \
				lambda c: Param_Currency.CURRNAMES[c][1])
			selectedIndex = 0
			for i, curr in enumerate(currencies):
				self.combo.addItem(
					Param_Currency.CURRNAMES[curr][1],
					curr)
				if curr == param.getDataInt():
					selectedIndex = i
			self.combo.setCurrentIndex(selectedIndex)
			self.combo.show()
		else:
			assert(0)

		self.changeBlocked -= 1

	def __comboChanged(self, index):
		if index < 0:
			return
		if self.changeBlocked:
			return
		if self.currentParam.getName() == "currency":
			curr = self.combo.itemData(index)
			self.currentParam.setData(curr)
		else:
			assert(0)

class GlobalParametersManageDialog(AbstractEntityManageDialog):
	"Global parameters modify dialog"

	def __init__(self, db, parent=None):
		self.editWidget = ParameterEditWidget()
		AbstractEntityManageDialog.__init__(self, db,
			"Global parameters", self.editWidget, parent,
			AbstractEntityManageDialog.HIDE_DELBUTTON |\
			AbstractEntityManageDialog.HIDE_NEWBUTTON |\
			AbstractEntityManageDialog.READONLY_DESC |\
			AbstractEntityManageDialog.READONLY_NAME |\
			AbstractEntityManageDialog.NO_PARAMETERS)

	def updateData(self, selectPart=None):
		AbstractEntityManageDialog.updateData(
			self, self.db.getUserParameters(),
			selectPart)

	def entSelChanged(self, item=None, prevItem=None):
		AbstractEntityManageDialog.entSelChanged(self,
			item, prevItem)
		param = item.getEntity() if item else None
		self.editWidget.updateData(param)
