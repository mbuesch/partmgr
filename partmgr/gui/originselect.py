# -*- coding: utf-8 -*-
#
# PartMgr GUI - Origin widgets
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

from partmgr.gui.protected_doublespinbox import *
from partmgr.gui.protected_lineedit import *
from partmgr.gui.itemselect import *
from partmgr.gui.groupselect import *
from partmgr.gui.storageselect import *
from partmgr.gui.util import *

from partmgr.core.origin import *
from partmgr.core.parameter import *


class PriceSpinBox(ProtectedDoubleSpinBox):
	def __init__(self, db, parent=None):
		ProtectedDoubleSpinBox.__init__(self, parent)
		self.setMinimum(Origin.NO_PRICE)
		self.setMaximum(16777215.0)
		self.setDecimals(2)
		self.setSingleStep(0.1)
		currency = db.getGlobalParameter("currency")
		currency = Param_Currency.CURRNAMES[currency.getDataInt()][0]
		self.setSuffix(" " + currency)

	def textFromValue(self, value):
		if value < 0.0:
			return "<no price>"
		return ProtectedDoubleSpinBox.textFromValue(self, value)

	def valueFromText(self, text):
		if text == "<no price>":
			return Origin.NO_PRICE
		return ProtectedDoubleSpinBox.valueFromText(self, text)

class OriginWidget(QWidget):
	codeChanged = Signal(str)
	priceChanged = Signal(float)

	def __init__(self, origin, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(QMargins())

		priceLayout = QGridLayout()

		label = QLabel("Price:", self)
		priceLayout.addWidget(label, 0, 0)

		price = origin.getPrice()
		self.price = PriceSpinBox(origin.db, self)
		self.price.setValue(Origin.NO_PRICE if price is None else price)
		priceLayout.addWidget(self.price, 0, 1)

		self.priceStamp = QLabel(self)
		font = self.priceStamp.font()
		font.setPointSize(8)
		self.priceStamp.setFont(font)
		priceLayout.addWidget(self.priceStamp, 1, 0, 1, 2)

		self.layout().addLayout(priceLayout)

		label = QLabel("Order code:", self)
		self.layout().addWidget(label)

		self.code = ProtectedLineEdit(self)
		self.code.setMinimumWidth(120)
		self.code.setText(origin.getOrderCode())
		self.layout().addWidget(self.code)

		self.code.textChanged.connect(self.codeChanged)
		self.price.valueChanged.connect(self.priceChanged)

		self.updatePriceStamp(origin)
		self.setProtected()

	def setProtected(self, prot=True):
		self.code.setProtected(prot)
		self.price.setProtected(prot)

	def updatePriceStamp(self, origin):
		priceStamp = origin.getPriceTimeStamp()
		self.priceStamp.clear()
		if priceStamp:
			self.priceStamp.setText(str(priceStamp))

class OneOriginSelectWidget(ItemSelectWidget):
	codeChanged = Signal(str)
	priceChanged = Signal(float)

	def __init__(self, origin, parent=None):
		self.originWidget = OriginWidget(origin)
		ItemSelectWidget.__init__(self, parent,
			actionButtonLabel = "Remove",
			itemLabel = None,
			itemSpecificWidget = self.originWidget)

		self.origin = origin
		self.updateData(origin.db.getSuppliers(),
			    origin.getSupplier())

		self.selectionChanged.connect(self.__supplierSelChanged)
		self.originWidget.codeChanged.connect(self.__orderCodeChanged)
		self.originWidget.codeChanged.connect(self.codeChanged)
		self.originWidget.priceChanged.connect(self.__priceChanged)
		self.originWidget.priceChanged.connect(self.priceChanged)

	def setProtected(self, prot=True):
		self.originWidget.setProtected(prot)
		ItemSelectWidget.setProtected(self, prot)

	def actionButtonPressed(self):
		supplier = self.origin.getSupplier()
		if supplier:
			supplier = supplier.getName()
		else:
			supplier = "<none>"
		orderCode = self.origin.getOrderCode()
		res = QMessageBox.question(self,
			"Delete origin?",
			"Delete the origin '%s' / '%s'?" %\
			(supplier, orderCode),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if res != QMessageBox.StandardButton.Yes:
			return

		self.origin.delete()
		self.selectionChanged.emit(None)
		self.parent().updateData()

	def __supplierSelChanged(self, supplier):
		self.origin.setSupplier(supplier)

	def __orderCodeChanged(self, newCode):
		self.origin.setOrderCode(newCode)

	def __priceChanged(self, newPrice):
		self.origin.setPrice(newPrice)
		self.originWidget.updatePriceStamp(self.origin)

class OriginsSelectWidget(GroupSelectWidget):
	selectionChanged = Signal()
	contentChanged = Signal()

	def __init__(self, parent=None):
		GroupSelectWidget.__init__(self, parent,
					   "Add new origin")
		self.currentStockItem = None

	def updateData(self, stockItem=None):
		if not stockItem:
			stockItem = self.currentStockItem
		self.clear()
		self.currentStockItem = stockItem
		origins = stockItem.getOrigins()
		origins.sort(key=lambda o: o.getId())
		for origin in origins:
			widget = OneOriginSelectWidget(origin, self)
			widget.selectionChanged.connect(self.selectionChanged)
			widget.selectionChanged.connect(self.contentChanged)
			widget.codeChanged.connect(self.contentChanged)
			widget.priceChanged.connect(self.contentChanged)
			self.addItemSelectWidget(widget)
		self.finishUpdate()

	def createNewGroup(self):
		stockItem = self.currentStockItem
		if not stockItem:
			return
		origin = Origin("", stockItem = stockItem)
		stockItem.db.modifyOrigin(origin)
		self.updateData(stockItem)
		self.contentChanged.emit()
