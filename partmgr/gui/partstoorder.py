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

		self.updateButton = QPushButton("&Update", self)
		self.layout().addWidget(self.updateButton, 1, 1)

		self.updateButton.released.connect(self.__updateTable)
		self.closeButton.released.connect(self.accept)
		self.orderTable.itemPressed.connect(self.__tabItemClicked)

		self.resize(750, 400)
		self.__updateTable()

	def __updateTable(self):
		self.orderTable.clear()

		stockItems = self.db.getStockItemsToPurchase()
		if not stockItems:
			self.orderTable.setRowCount(1)
			self.orderTable.setColumnCount(1)
			self.orderTable.setColumnWidth(0, 400)
			item = QTableWidgetItem("No items to purchase found.",
						QTableWidgetItem.ItemType.Type)
			item.setData(Qt.ItemDataRole.UserRole, None)
			self.orderTable.setItem(0, 0, item)
			return

		# Build the table
		columns = (("Item name", 200), ("Order codes", 220),
			   ("Amount to order", 120), ("Cur. in stock", 120))
		self.orderTable.setColumnCount(len(columns))
		self.orderTable.setRowCount(len(stockItems))
		self.orderTable.setHorizontalHeaderLabels(tuple(l[0] for l in columns))
		for i, (colName, colWidth) in enumerate(columns):
			self.orderTable.setColumnWidth(i, colWidth)

		# Populate the table
		for i, stockItem in enumerate(stockItems):
			def mkitem(text):
				item = QTableWidgetItem(text, QTableWidgetItem.ItemType.Type)
				item.setData(Qt.ItemDataRole.UserRole, stockItem.getId())
				return item

			self.orderTable.setRowHeight(i, 50)

			self.orderTable.setItem(i, 0,
						mkitem(stockItem.getName()))
			orderCodes = []
			for origin in stockItem.getOrigins():
				code = ""
				supplier = origin.getSupplier()
				if supplier:
					code += supplier.getName() + ": "
				if origin.getOrderCode():
					code += origin.getOrderCode()
				else:
					code += "<no order code>"
				orderCodes.append(code)
			self.orderTable.setItem(i, 1,
						mkitem("\n".join(orderCodes)))
			self.orderTable.setItem(i, 2,
						mkitem("%d %s" % (
						       stockItem.getOrderQuantity(),
						       stockItem.getQuantityUnitsShort())))
			self.orderTable.setItem(i, 3,
						mkitem("%d %s" % (
						       stockItem.getGlobalQuantity(),
						       stockItem.getQuantityUnitsShort())))

	def __tabItemClicked(self, item):
		if not item:
			return
		itemData = item.data(Qt.ItemDataRole.UserRole)
		if itemData is None:
			return

		mouseButtons = QApplication.mouseButtons()
		if mouseButtons & Qt.MouseButton.RightButton:
			if self.orderTable.currentColumn() == 1:
				stockItem = self.db.getStockItem(itemData)
				menu = QMenu()
				count = 0
				for origin in stockItem.getOrigins():
					supp = origin.getSupplier()
					orderCode = origin.getOrderCode()
					if not supp or not orderCode:
						continue
					suppName = supp.getName()
					if not suppName:
						continue
					menu.addAction("Copy '%s' order "
						"code" % suppName,
						lambda code = orderCode:
							copyStrToClipboard(code))
					count += 1
				if count:
					menu.exec(QCursor.pos())
