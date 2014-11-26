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
		self.setMinimum(-16777215.0)
		self.setMaximum(16777215.0)
		self.setDecimals(2)
		self.setSingleStep(0.1)
		currency = db.getParameterByName("currency")
		currency = Param_Currency.CURRNAMES[currency.getDataInt()][0]
		self.setSuffix(" " + currency)

class OriginWidget(QWidget):
	codeChanged = Signal(str)
	priceChanged = Signal(float)

	def __init__(self, origin, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(QMargins())

		priceLayout = QHBoxLayout()

		label = QLabel("Price:", self)
		priceLayout.addWidget(label)

		self.price = PriceSpinBox(origin.db, self)
		self.price.setValue(origin.getPrice())
		priceLayout.addWidget(self.price)

		self.layout().addLayout(priceLayout)

		label = QLabel("Order code:", self)
		self.layout().addWidget(label)

		self.code = ProtectedLineEdit(self)
		self.code.setMinimumWidth(120)
		self.code.setText(origin.getOrderCode())
		self.layout().addWidget(self.code)

		self.code.textChanged.connect(self.codeChanged)
		self.price.valueChanged.connect(self.priceChanged)

		self.setProtected()

	def setProtected(self, prot=True):
		self.code.setProtected(prot)
		self.price.setProtected(prot)

class OneOriginSelectWidget(ItemSelectWidget):
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
		self.originWidget.codeChanged.connect(
				self.__orderCodeChanged)
		self.originWidget.priceChanged.connect(
				self.__priceChanged)

	def setProtected(self, prot=True):
		self.originWidget.setProtected(prot)
		ItemSelectWidget.setProtected(self, prot)

	def actionButtonPressed(self):
		self.origin.delete()
		self.selectionChanged.emit(None)
		self.parent().updateData()

	def __supplierSelChanged(self, supplier):
		self.origin.setSupplier(supplier)

	def __orderCodeChanged(self, newCode):
		self.origin.setOrderCode(newCode)

	def __priceChanged(self, newPrice):
		self.origin.setPrice(newPrice)

class OriginsSelectWidget(GroupSelectWidget):
	selectionChanged = Signal()

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
			self.addItemSelectWidget(widget)
		self.finishUpdate()

	def createNewGroup(self):
		stockItem = self.currentStockItem
		if not stockItem:
			return
		origin = Origin("", stockItem = stockItem)
		stockItem.db.modifyOrigin(origin)
		self.updateData(stockItem)
