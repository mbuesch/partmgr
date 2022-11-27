# -*- coding: utf-8 -*-
#
# PartMgr GUI - Price fetching
#
# Copyright 2015 Michael Buesch <m@bues.ch>
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

from partmgr.core.database import *
from partmgr.core.parameter import *

from partmgr.pricefetch import *

from partmgr.gui.util import *


class PriceFetchDialog(QDialog):
	def __init__(self, db, parent=None):
		QDialog.__init__(self, parent)
		self.setLayout(QGridLayout())
		self.setWindowTitle("Parts manager - Price fetcher")

		self.db = db

		self.fetchMissingRadio = QRadioButton("Set &missing prices only", self)
		self.layout().addWidget(self.fetchMissingRadio, 0, 0, 1, 4)

		self.updateAllRadio = QRadioButton("Update &all prices", self)
		self.layout().addWidget(self.updateAllRadio, 1, 0, 1, 4)

		self.fetchButton = QPushButton("&Fetch prices from supplier...", self)
		self.layout().addWidget(self.fetchButton, 0, 3, 2, 1)

		self.table = QTableWidget(self)
		self.layout().addWidget(self.table, 2, 0, 1, 4)

		self.resultLine = QLabel(self)
		self.layout().addWidget(self.resultLine, 3, 0, 1, 3)

		self.statusLine = QLabel(self)
		self.layout().addWidget(self.statusLine, 4, 0, 1, 3)

		self.stopButton = QPushButton("&Stop", self)
		self.stopButton.hide()
		self.layout().addWidget(self.stopButton, 3, 3, 2, 1)

		self.closeButton = QPushButton("&Close", self)
		self.layout().addWidget(self.closeButton, 5, 3)

		self.table.itemPressed.connect(self.__tabItemClicked)
		self.fetchMissingRadio.toggled.connect(self.__rebuildTable)
		self.updateAllRadio.toggled.connect(self.__rebuildTable)
		self.fetchButton.released.connect(self.__fetch)
		self.stopButton.pressed.connect(self.__stop)
		self.closeButton.released.connect(self.accept)

		self.fetchMissingRadio.setChecked(True)
		self.resize(850, 600)

	def __doFetch(self):
		self.resultLine.clear()
		self.statusLine.setText("Preparing to fetch prices...")
		QApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents |
					   QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents,
					   250)

		# Filter the table and build a dict of lists.
		toFetch = {}
		for tableRow in range(self.table.rowCount()):
			tableItem = self.table.item(tableRow, 0)

			origin = self.db.getOrigin(tableItem.data(Qt.ItemDataRole.UserRole))
			if not origin:
				continue
			orderCode = origin.getOrderCode()
			if not orderCode.strip():
				continue
			supplier = origin.getSupplier()
			if not supplier:
				continue
			supplierName = supplier.getName()
			if not supplierName.strip():
				continue

			toFetch.setdefault(supplierName, []).append(
				(tableItem, orderCode))

		def relax(*args):
			QApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 250)

		# Fetch the prices.
		for supplierName in sorted(toFetch):
			try:
				fetcherCls = PriceFetcher.get(supplierName)
				if not fetcherCls:
					continue
				fetcherCls._relax = relax
				fetcher = fetcherCls()
			except PriceFetcher.Error as e:
				continue

			count = 0

			def preCallback(orderCode):
				nonlocal count
				tableItem, orderCode = toFetch[supplierName][count]
				self.statusLine.setText("Fetching '%s' from %s..." % (
					orderCode, supplierName))
				relax()

			def postCallback(orderCode):
				nonlocal count
				count += 1

			orderCodes = (orderCode
				      for tableRow, orderCode in toFetch[supplierName])
			for priceResult in fetcher.getPrices(orderCodes,
							     preCallback=preCallback,
							     postCallback=postCallback):
				tableItem, orderCode = toFetch[supplierName][count]
				origin = self.db.getOrigin(tableItem.data(Qt.ItemDataRole.UserRole))
				self.__setPriceResult(supplierName, tableItem, orderCode,
						      origin, priceResult)
				relax()
				if self.__stopRequested:
					break
		self.resultLine.clear()
		self.statusLine.setText("Aborted." if self.__stopRequested else "Done.")

	def __setPriceResult(self, supplierName, tableItem,
			     orderCode, origin, priceResult):
		requiredCurrency = self.db.getGlobalParameter("currency").getDataInt()
		requiredCurrencyStr = Param_Currency.CURRNAMES[requiredCurrency][0]

		if priceResult.status != priceResult.FOUND:
			text = "Did not find '%s' on %s." % (\
				orderCode, supplierName)
			self.resultLine.setText(text)
			print("Price fetch error: %s" % text)
			return
		if priceResult.currency != requiredCurrency:
			text = "Got '%s' from %s, "\
				"but it has the wrong currency." % (\
				orderCode, supplierName)
			self.resultLine.setText(text)
			print("Price fetch error: %s" % text)
			return
		priceStr = "%.2f %s" % (priceResult.price,
					requiredCurrencyStr)
		self.resultLine.setText("Successfully fetched '%s' from %s: %s" % (
			orderCode, supplierName, priceStr))

		origin.setPrice(priceResult.price)
		self.table.setItem(tableItem.row(), 4,
				   self.__tabItem(priceStr, origin))

	def __setUiEnabled(self, enable):
		self.fetchMissingRadio.setEnabled(enable)
		self.updateAllRadio.setEnabled(enable)
		self.fetchButton.setEnabled(enable)
		self.closeButton.setEnabled(enable)

	def __fetch(self):
		self.__rebuildTable()
		try:
			self.__setUiEnabled(False)
			self.__stopRequested = False
			self.stopButton.show()
			self.__doFetch()
		except PriceFetcher.Error as e:
			QMessageBox.critical(self,
				"Price fetching failed",
				"Price fetching failed:\n%s" % str(e))
		finally:
			self.__setUiEnabled(True)
			self.stopButton.hide()

	def __stop(self):
		self.__stopRequested = True
		self.stopButton.hide()
		self.statusLine.setText("Stopping...")
		QApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 250)

	def __tabItem(self, text, origin):
		item = QTableWidgetItem(text, QTableWidgetItem.ItemType.UserType)
		item.setFlags(Qt.ItemFlag.ItemIsSelectable |\
			      Qt.ItemFlag.ItemIsEnabled)
		item.setData(Qt.ItemDataRole.UserRole, origin.getId())
		return item

	def __rebuildTable(self):
		if self.fetchMissingRadio.isChecked():
			stockItems = self.db.getStockItemsWithMissingPrice()
		elif self.updateAllRadio.isChecked():
			stockItems = self.db.getAllStockItems()
		else:
			assert(0)

		self.table.setSortingEnabled(False)
		self.table.clear()
		self.table.setRowCount(0)
		columns = (("Stock item", 250), ("Supplier", 120),
			   ("Order code", 160),
			   ("Old price", 100), ("New price", 100))
		self.table.setColumnCount(len(columns))
		self.table.setHorizontalHeaderLabels(tuple(l[0] for l in columns))
		for i, (colName, colWidth) in enumerate(columns):
			self.table.setColumnWidth(i, colWidth)

		i = 0
		for stockItem in stockItems:
			for origin in stockItem.getOrigins():
				self.table.setRowCount(self.table.rowCount() + 1)

				stockItemName = stockItem.getName()
				supplier = origin.getSupplier()
				supplierName = supplier.getName() if supplier else ""
				orderCode = origin.getOrderCode()
				currency = self.db.getGlobalParameter("currency")
				currency = Param_Currency.CURRNAMES[currency.getDataInt()][0]
				price = origin.getPrice()
				price = ("%.2f %s" % (price, currency))\
					if price else "<none>"

				self.table.setItem(i, 0,
						   self.__tabItem(stockItemName, origin))
				self.table.setItem(i, 1,
						   self.__tabItem(supplierName, origin))
				self.table.setItem(i, 2,
						   self.__tabItem(orderCode, origin))
				self.table.setItem(i, 3,
						   self.__tabItem(price, origin))
				i += 1
		self.table.setSortingEnabled(True)

	def __tabItemClicked(self, item):
		if not item:
			return

		mouseButtons = QApplication.mouseButtons()
		if mouseButtons & Qt.MouseButton.RightButton:
			menu = QMenu()
			menu.addAction("Copy",
				       lambda text = item.text():
						copyStrToClipboard(text))
			menu.exec(QCursor.pos())
