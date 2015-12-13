# -*- coding: utf-8 -*-
#
# PartMgr GUI - Parts-to-order dialog
#
# Copyright 2014-2015 Michael Buesch <m@bues.ch>
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


class PartsToOrderDialog(QDialog):
	def __init__(self, db, parent=None):
		QDialog.__init__(self, parent)
		self.setLayout(QGridLayout())
		self.setWindowTitle("Parts manager - Parts to order")

		self.db = db

		self.orderTable = QTableWidget(self)
		self.layout().addWidget(self.orderTable, 0, 0, 1, 3)

		self.closeButton = QPushButton("&Close", self)
		self.layout().addWidget(self.closeButton, 1, 2)

		self.closeButton.released.connect(self.accept)

		self.resize(750, 400)
		self.__updateTable()

		#TODO context menu to copy order codes

	def __updateTable(self):
		self.orderTable.clear()

		stockItems = self.db.getStockItemsToPurchase()
		if not stockItems:
			self.orderTable.setRowCount(1)
			self.orderTable.setColumnCount(1)
			self.orderTable.setItem(0, 0,
				QTableWidgetItem("No items to purchase found.",
						 QTableWidgetItem.Type))
			return

		self.orderTable.setColumnCount(3)
		self.orderTable.setRowCount(len(stockItems))
		self.orderTable.setHorizontalHeaderLabels(
			("Item name", "Order codes", "Amount to order"))
		self.orderTable.setColumnWidth(0, 200)
		self.orderTable.setColumnWidth(1, 220)
		self.orderTable.setColumnWidth(2, 120)

		for i, stockItem in enumerate(stockItems):
			self.orderTable.setRowHeight(i, 50)
			self.orderTable.setItem(i, 0,
				QTableWidgetItem(stockItem.getVerboseName(),
						 QTableWidgetItem.Type))
			orderCodes = []
			for origin in stockItem.getOrigins():
				code = ""
				supplier = origin.getSupplier()
				if supplier:
					code += supplier.getVerboseName() + ": "
				if origin.getOrderCode():
					code += origin.getOrderCode()
				else:
					code += "<no order code>"
				orderCodes.append(code)
			self.orderTable.setItem(i, 1,
				QTableWidgetItem("\n".join(orderCodes),
						 QTableWidgetItem.Type))
			self.orderTable.setItem(i, 2,
				QTableWidgetItem("%d %s" % (
					stockItem.getOrderQuantity(),
					stockItem.getQuantityUnitsShort())))
