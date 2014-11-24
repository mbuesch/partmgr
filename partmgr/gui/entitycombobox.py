# -*- coding: utf-8 -*-
#
# PartMgr GUI - Entity combo box
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

from partmgr.gui.protected_combobox import *
from partmgr.gui.util import *

from partmgr.core.entity import *


class EntityComboBox(ProtectedComboBox):
	def __init__(self, parent=None):
		ProtectedComboBox.__init__(self, parent)

		self.updateBlocked = 0

	def updateData(self, entities, selected=None):
		if self.updateBlocked:
			return
		self.updateBlocked += 1

		ProtectedComboBox.clear(self)
		self.addItem("-- None --", Entity())
		selectedIndex = 0
		for i, entity in enumerate(entities):
			self.addItem(entity.getName(), entity)
			if selected and selected == entity:
				selectedIndex = i + 1
		self.setCurrentIndex(selectedIndex)

		self.updateBlocked -= 1

	def clear(self):
		self.updateData([])

	def getSelectedEntity(self):
		index = self.currentIndex()
		if index >= 0:
			return self.itemData(index)
		return None

	def setSelectedEntity(self, entity):
		index = self.findData(entity)
		if index >= 0:
			self.setCurrentIndex(index)
