# -*- coding: utf-8 -*-
#
# PartMgr GUI - Item select widget
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

from partmgr.gui.entitycombobox import *
from partmgr.gui.util import *

from partmgr.core.entity import *


class ItemSelectWidget(QWidget):
	"Abstract item selection widget"

	selectionChanged = Signal(object)

	def __init__(self, parent=None,
		     actionButtonLabel=None,
		     itemLabel=None,
		     itemSpecificWidget=None):
		QWidget.__init__(self, parent)

		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(QMargins(0, 5, 0, 5))
		x = 0

		comboLayout = QVBoxLayout()

		if itemLabel:
			self.itemLabel = QLabel(itemLabel, self)
			comboLayout.addWidget(self.itemLabel)

		self.combo = EntityComboBox(self)
		comboLayout.addWidget(self.combo)

		comboLayout.addStretch(1)

		comboWidth = 4 if itemSpecificWidget else 8
		self.layout().addLayout(comboLayout,
					0, x, 1, comboWidth)
		x += comboWidth

		if itemSpecificWidget:
			self.layout().addWidget(itemSpecificWidget,
						0, x, 1, 4)
			x += 4

		if actionButtonLabel:
			self.actionButton = QPushButton(actionButtonLabel,
							self)
			self.layout().addWidget(self.actionButton,
						0, x, 1, 1)
			x += 1
			self.actionButton.released.connect(
					self.actionButtonPressed)

		self.descLabel = QLabel(self)
		self.descLabel.hide()
		self.layout().addWidget(self.descLabel, 1, 0, 1, x)

		self.setProtected()

		self.combo.currentIndexChanged.connect(
					self.__idxChanged)

	def setProtected(self, prot=True):
		self.combo.setProtected(prot)
		try:
			self.actionButton.setEnabled(not prot)
		except AttributeError as e:
			pass

	def updateData(self, entities, selected=None):
		self.combo.updateData(entities, selected)

	def clear(self):
		self.combo.clear()

	def getSelected(self):
		return self.combo.getSelectedEntity()

	def setSelected(self, entity):
		self.combo.setSelectedEntity(entity)

	def __idxChanged(self, comboIndex):
		entity = self.combo.itemData(comboIndex)
		description = entity.getDescription() if entity else None
		if description:
			self.descLabel.setText(description)
			self.descLabel.show()
		else:
			self.descLabel.hide()
		self.selectionChanged.emit(entity)

	def actionButtonPressed(self):
		raise NotImplementedError
