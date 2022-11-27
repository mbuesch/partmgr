# -*- coding: utf-8 -*-
#
# PartMgr GUI - Storage widgets
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

from partmgr.gui.itemselect import *
from partmgr.gui.groupselect import *
from partmgr.gui.quantity import *
from partmgr.gui.util import *

from partmgr.core.storage import *


class OneStorageSelectWidget(ItemSelectWidget):
	quantityChanged = Signal(int)

	def __init__(self, storage, parent=None):
		self.quantity = QuantityWidget(storage)
		ItemSelectWidget.__init__(self, parent,
			actionButtonLabel = "Remove",
			itemLabel = "Location:",
			itemSpecificWidget = self.quantity)

		self.storage = storage
		self.updateData(storage.db.getLocations(),
			    storage.getLocation())

		self.selectionChanged.connect(self.__locationSelChanged)
		self.quantity.quantityChanged.connect(self.__quantityChanged)

	def __locationSelChanged(self, location):
		self.storage.setLocation(location)

	def __quantityChanged(self, newQuantity):
		self.storage.setQuantity(newQuantity)
		self.quantityChanged.emit(newQuantity)

	def actionButtonPressed(self):
		qty = str(self.storage.getQuantity())
		loc = self.storage.getLocation()
		if loc:
			loc = loc.getName()
		else:
			loc = "<none>"
		res = QMessageBox.question(self,
			"Delete storage?",
			"Delete the storage '%s' / '%s'?" %\
			(loc, qty),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if res != QMessageBox.StandardButton.Yes:
			return

		self.storage.delete()
		self.quantityChanged.emit(0)
		self.parent().updateData()

class StoragesSelectWidget(GroupSelectWidget):
	quantityChanged = Signal()
	contentChanged = Signal()

	def __init__(self, parent=None):
		GroupSelectWidget.__init__(self, parent,
					   "Add new storage")
		self.currentStockItem = None

	def updateData(self, stockItem=None):
		if not stockItem:
			stockItem = self.currentStockItem
		self.clear()
		self.currentStockItem = stockItem
		storages = stockItem.getStorages()
		storages.sort(key=lambda s: s.getId())
		for storage in storages:
			widget = OneStorageSelectWidget(storage, self)
			widget.selectionChanged.connect(self.contentChanged)
			widget.quantityChanged.connect(self.quantityChanged)
			self.addItemSelectWidget(widget)
		self.finishUpdate()

	def createNewGroup(self):
		stockItem = self.currentStockItem
		if not stockItem:
			return
		storage = Storage("", stockItem = stockItem)
		stockItem.db.modifyStorage(storage)
		self.updateData(stockItem)
		self.contentChanged.emit()
