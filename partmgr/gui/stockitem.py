# -*- coding: utf-8 -*-
#
# PartMgr GUI - Stock item window
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

from partmgr.gui.partselect import *
from partmgr.gui.footprintselect import *
from partmgr.gui.originselect import *
from partmgr.gui.util import *

from partmgr.core.stockitem import *


class StockItemWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(QMargins())

		leftLayout = QGridLayout()
		leftLayout.setContentsMargins(QMargins(5, 0, 10, 0))
		rightLayout = QGridLayout()
		rightLayout.setContentsMargins(QMargins(10, 0, 0, 0))

		self.partGroup = QGroupBox("Part", self)
		self.partGroup.setLayout(QGridLayout(self.partGroup))
		self.partSel = PartSelectWidget(self)
		self.partGroup.layout().addWidget(self.partSel, 0, 0)
		footpLayout = QHBoxLayout()
		self.footpImage = QLabel(self)
		footpLayout.addWidget(self.footpImage)
		self.footpSel = FootprintSelectWidget(self)
		footpLayout.addWidget(self.footpSel)
		footpLayout.addStretch()
		self.partGroup.layout().addLayout(footpLayout, 1, 0)
		leftLayout.addWidget(self.partGroup, 0, 0)

		self.originGroup = QGroupBox("Origins / Suppliers", self)
		self.originGroup.setLayout(QGridLayout(self.originGroup))
		self.originsSel = OriginsSelectWidget(self)
		self.originGroup.layout().addWidget(self.originsSel, 0, 0)
		leftLayout.addWidget(self.originGroup, 1, 0)

		self.storageGroup = QGroupBox("Storages", self)
		self.storageGroup.setLayout(QGridLayout(self.storageGroup))
		self.storagesSel = StoragesSelectWidget(self)
		self.storageGroup.layout().addWidget(self.storagesSel, 0, 0)
		rightLayout.addWidget(self.storageGroup, 0, 0)

		self.quantityGroup = QGroupBox("Global quantity", self)
		self.quantityGroup.setLayout(QGridLayout(self.quantityGroup))
		label = QLabel("Global stock qty:", self)
		self.quantityGroup.layout().addWidget(label, 0, 0)
		globQtyLayout = QHBoxLayout()
		self.globalQuantity = QLabel(self)
		self.globalQuantity.setFrameShape(QFrame.Shape.Panel)
		self.globalQuantity.setFrameShadow(QFrame.Shadow.Sunken)
		font = self.globalQuantity.font()
		font.setBold(True)
		self.globalQuantity.setFont(font)
		globQtyLayout.addWidget(self.globalQuantity)
		self.quantityUnitsCombo = ProtectedComboBox(self)
		for unit in StockItem.getAllQuantityUnits():
			self.quantityUnitsCombo.addItem(
				StockItem.quantityLongName(unit),
				unit)
		globQtyLayout.addStretch()
		globQtyLayout.addWidget(self.quantityUnitsCombo)
		self.quantityGroup.layout().addLayout(globQtyLayout, 0, 1)
		label = QLabel("Minimum in stock:", self)
		self.quantityGroup.layout().addWidget(label, 1, 0)
		self.minQuantitySpinBox = QuantitySpinBox(self)
		self.minQuantitySpinBox.setKeyboardTracking(False)
		self.quantityGroup.layout().addWidget(
			self.minQuantitySpinBox, 1, 1)
		label = QLabel("Target stock:", self)
		self.quantityGroup.layout().addWidget(label, 2, 0)
		self.targetQuantitySpinBox = QuantitySpinBox(self)
		self.targetQuantitySpinBox.setKeyboardTracking(False)
		self.quantityGroup.layout().addWidget(
			self.targetQuantitySpinBox, 2, 1)
		rightLayout.addWidget(self.quantityGroup, 1, 0)

		self.datesLabel = QLabel(self)
		font = self.datesLabel.font()
		font.setPointSize(8)
		self.datesLabel.setFont(font)
		self.datesLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
		rightLayout.addWidget(self.datesLabel, 2, 0)

		leftLayout.setRowStretch(100, 1)
		rightLayout.setRowStretch(100, 1)

		self.layout().addLayout(leftLayout, 0, 0)
		self.layout().addLayout(rightLayout, 0, 1)

		self.layout().setColumnStretch(100, 1)

		self.partSel.selectionChanged.connect(
			self.__partSelChanged)
		self.footpSel.selectionChanged.connect(
			self.__footpSelChanged)
		self.originsSel.contentChanged.connect(
			self.__updateModDates)
		self.storagesSel.quantityChanged.connect(
			self.__updateQuantity)
		self.storagesSel.quantityChanged.connect(
			self.__updateModDates)
		self.storagesSel.contentChanged.connect(
			self.__updateModDates)
		self.quantityUnitsCombo.currentIndexChanged.connect(
			self.__quantityUnitsChanged)
		self.minQuantitySpinBox.valueChanged.connect(
			self.__minQuantityChanged)
		self.targetQuantitySpinBox.valueChanged.connect(
			self.__targetQuantityChanged)

		self.modifyBlocked = 0

		self.setStockItem(None)
		index = self.quantityUnitsCombo.currentIndex()
		self.__quantityUnitsChanged(index)

	def setProtected(self, prot=True):
		self.partSel.setProtected(prot)
		self.footpSel.setProtected(prot)
		self.originsSel.setProtected(prot)
		self.storagesSel.setProtected(prot)
		self.quantityUnitsCombo.setProtected(prot)
		self.minQuantitySpinBox.setProtected(prot)
		self.targetQuantitySpinBox.setProtected(prot)

	def __updateModDates(self):
		self.modifyBlocked += 1

		stockItem = self.currentItem
		if not stockItem:
			self.datesLabel.clear()

			self.modifyBlocked -= 1
			return

		def mkstamp(stamp):
			if stamp:
				return stamp
			return datetime.datetime(2000, 1, 1)

		createStamp = mkstamp(stockItem.getCreateTimeStamp())
		modTimes = []
		modTimes.append(mkstamp(stockItem.getModifyTimeStamp()))
		part = stockItem.getPart()
		if part:
			modTimes.append(mkstamp(part.getModifyTimeStamp()))
		for origin in stockItem.getOrigins():
			modTimes.append(mkstamp(origin.getModifyTimeStamp()))
			modTimes.append(mkstamp(origin.getPriceTimeStamp()))
		for storage in stockItem.getStorages():
			modTimes.append(mkstamp(storage.getModifyTimeStamp()))
		modStamp = max(modTimes)

		self.datesLabel.setText("created: %s\n"
				        "modified: %s" %\
					(createStamp, modStamp))

		self.modifyBlocked -= 1

	def __updateQuantity(self):
		self.modifyBlocked += 1

		stockItem = self.currentItem
		if not stockItem:
			self.quantityUnitsCombo.setCurrentIndex(0)
			self.globalQuantity.clear()
			self.minQuantitySpinBox.setValue(0)
			self.targetQuantitySpinBox.setValue(0)

			self.modifyBlocked -= 1
			return

		unitSuffix = " " + stockItem.getQuantityUnitsShort()
		index = self.quantityUnitsCombo.findData(
				stockItem.getQuantityUnits())
		self.quantityUnitsCombo.setCurrentIndex(index)
		self.globalQuantity.setText(
				str(stockItem.getGlobalQuantity()))
		self.minQuantitySpinBox.setSuffix(unitSuffix)
		self.minQuantitySpinBox.setValue(
				stockItem.getMinQuantity())
		self.targetQuantitySpinBox.setSuffix(unitSuffix)
		self.targetQuantitySpinBox.setValue(
				stockItem.getTargetQuantity())

		self.modifyBlocked -= 1

	def updateData(self):
		self.modifyBlocked += 1

		self.__updateQuantity()
		self.__updateModDates()

		stock = self.currentItem
		if not stock:
			self.partSel.clear()
			self.footpSel.clear()
			self.footpImage.clear()
			self.footpImage.hide()
			self.storagesSel.clear()
			self.originsSel.clear()
			self.setEnabled(False)

			self.modifyBlocked -= 1
			return
		self.partSel.updateData(stock)
		self.footpSel.updateData(stock.db)
		part = stock.getPart()
		self.partSel.setSelected(part)
		footp = stock.getFootprint()
		self.footpSel.setSelected(footp)
		image = footp.getImage() if footp else None
		if not image or image.isNull():
			self.footpImage.clear()
			self.footpImage.hide()
		else:
			image = image.scaleToMaxSize(QSize(50, 50))
			self.footpImage.setPixmap(image.toPixmap())
			self.footpImage.show()
		self.storagesSel.updateData(stock)
		self.originsSel.updateData(stock)
		self.setEnabled(True)

		self.modifyBlocked -= 1

	def setStockItem(self, item):
		self.currentItem = item
		self.updateData()

	def __quantityUnitsChanged(self, index):
		if self.modifyBlocked:
			return
		if self.currentItem:
			unit = self.quantityUnitsCombo.itemData(index)
			self.currentItem.setQuantityUnits(unit)
		self.updateData()

	def __minQuantityChanged(self, newValue):
		if self.modifyBlocked:
			return
		stockItem = self.currentItem
		if not stockItem:
			return
		stockItem.setMinQuantity(newValue)
		if newValue > stockItem.getTargetQuantity():
			self.targetQuantitySpinBox.setValue(newValue)

	def __targetQuantityChanged(self, newValue):
		if self.modifyBlocked:
			return
		stockItem = self.currentItem
		if not stockItem:
			return
		stockItem.setTargetQuantity(newValue)
		if newValue < stockItem.getMinQuantity():
			self.minQuantitySpinBox.setValue(newValue)

	def __partSelChanged(self, part):
		if self.modifyBlocked:
			return
		stockItem = self.currentItem
		if not stockItem:
			return
		stockItem.setPart(part)
		self.updateData()

	def __footpSelChanged(self, footprint):
		if self.modifyBlocked:
			return
		stockItem = self.currentItem
		if not stockItem:
			return
		stockItem.setFootprint(footprint)
		self.updateData()
