# -*- coding: utf-8 -*-
#
# PartMgr GUI - Global stats dialog
#
# Copyright 2014-2026 Michael Büsch <m@bues.ch>
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
from partmgr.core.parameter import Param_Currency


def _currencyName(param):
	"""Convert the global currency parameter to a short currency name.
	"""
	if not param:
		return ""
	try:
		idx = param.getDataInt()
	except PartMgrError:
		return ""
	return Param_Currency.CURRNAMES.get(idx, ("?", "?"))[0]

def calculateGlobalStats(db):
	"""Calculate global statistics for a database.
	"""
	stats = {}

	stockItems = db.getAllStockItems()

	stats["total_parts"] = db.countParts()
	stats["total_stock_items"] = len(stockItems)
	stats["total_categories"] = db.countCategories()
	stats["total_suppliers"] = db.countSuppliers()
	stats["total_locations"] = db.countLocations()
	stats["total_footprints"] = db.countFootprints()

	totalQuantity = 0
	totalValue = 0.0
	for stockItem in stockItems:
		origins = stockItem.getOrigins()
		quantity = stockItem.getGlobalQuantity()
		totalQuantity += quantity
		prices = [
			origin.getEffectivePrice()
			for origin in origins
			if origin.hasPrice()
		]
		if prices:
			totalValue += min(prices) * quantity

	stats["total_locations"] = db.countLocations()
	stats["total_quantity"] = totalQuantity
	stats["total_value"] = round(totalValue, 2)
	stats["items_missing_price"] = len(db.getStockItemsWithMissingPrice())
	stats["items_to_order"] = len(db.getStockItemsToPurchase())
	stats["currency"] = _currencyName(db.getGlobalParameter("currency"))

	return stats


class GlobalStatsDialog(QDialog):
	"""Dialog that displays global database statistics."""

	def __init__(self, db, parent=None):
		QDialog.__init__(self, parent)
		self.db = db

		self.setWindowTitle("Parts manager - Global statistics")
		self.setLayout(QVBoxLayout())

		self.formLayout = QFormLayout()
		self.layout().addLayout(self.formLayout)

		buttonLayout = QHBoxLayout()
		buttonLayout.addStretch()

		self.updateButton = QPushButton("&Update", self)
		self.closeButton = QPushButton("&Close", self)
		buttonLayout.addWidget(self.updateButton)
		buttonLayout.addWidget(self.closeButton)
		self.layout().addLayout(buttonLayout)

		self.closeButton.released.connect(self.accept)
		self.updateButton.released.connect(self.__update)

		self.resize(400, 380)
		self.__update()

	def __update(self):
		"""Refresh the displayed statistics."""
		# Remove existing rows.
		while self.formLayout.rowCount() > 0:
			self.formLayout.removeRow(0)

		stats = calculateGlobalStats(self.db)

		rows = (
			("Total parts", str(stats["total_parts"])),
			("Total stock items", str(stats["total_stock_items"])),
			("Total categories", str(stats["total_categories"])),
			("Total suppliers", str(stats["total_suppliers"])),
			("Total locations", str(stats["total_locations"])),
			("Total footprints", str(stats["total_footprints"])),
			("Total quantity in stock",
			 "%d" % stats["total_quantity"]),
			("Items missing price",
			 "%d" % stats["items_missing_price"]),
			("Items to order",
			 "%d" % stats["items_to_order"]),
			("Total inventory value",
			 "%.2f %s" % (stats["total_value"], stats["currency"])),
		)

		for label, value in rows:
			valueLabel = QCopyLabel(value, self)
			self.formLayout.addRow(label + ":", valueLabel)
