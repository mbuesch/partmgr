# -*- coding: utf-8 -*-
#
# PartMgr GUI - Main window
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

from partmgr.gui.tree import *
from partmgr.gui.stockitem import *
from partmgr.gui.partselect import *
from partmgr.gui.partstoorder import *
from partmgr.gui.globalstats import *
from partmgr.gui.partmanage import *
from partmgr.gui.footprintmanage import *
from partmgr.gui.locationmanage import *
from partmgr.gui.suppliermanage import *
from partmgr.gui.parametermanage import *
from partmgr.gui.util import *

from partmgr.core.database import *


class PartMgrMainWidget(QWidget):
	def __init__(self, db, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.db = db

		self.tree = Tree(db, self)
		self.tree.setMinimumWidth(150)
		self.layout().addWidget(self.tree, 0, 0, 2, 1)

		self.stock = StockItemWidget(self)
		self.layout().addWidget(self.stock, 0, 1, 1, 1)

		self.editEnable = QCheckBox("Edit", self)
		self.layout().addWidget(self.editEnable, 1, 1, 1, 1)

		self.tree.itemChanged.connect(self.itemChanged)
		self.editEnable.stateChanged.connect(self.__editChanged)

	def __editChanged(self, newState):
		self.stock.setProtected(newState != Qt.Checked)

	def itemChanged(self, stockItemId):
		stockItem = None
		if Entity.isValidId(stockItemId):
			stockItem = self.db.getStockItem(stockItemId)
		self.stock.setStockItem(stockItem)
		self.editEnable.setEnabled(bool(stockItem))

	def shutdown(self):
		self.db.close()

	def showGlobalStats(self):
		dlg = GlobalStatsDialog(self.db, self)
		dlg.exec_()

	def showPartsToOrder(self):
		dlg = PartsToOrderDialog(self.db, self)
		dlg.exec_()

	def manageGlobalParams(self):
		dlg = GlobalParametersManageDialog(self.db, self)
		dlg.edit()
		self.stock.update()

	def manageParts(self):
		dlg = PartManageDialog(self.db, self)
		dlg.edit()
		self.stock.update()

	def manageFootprints(self):
		dlg = FootprintManageDialog(self.db, self)
		dlg.edit()
		self.stock.update()

	def manageLocations(self):
		dlg = LocationManageDialog(self.db, self)
		dlg.edit()
		self.stock.update()

	def manageSuppliers(self):
		dlg = SupplierManageDialog(self.db, self)
		dlg.edit()
		self.stock.update()

class PartMgrMainWindow(QMainWindow):
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)

		self.setMenuBar(QMenuBar(self))

		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction("&Load database...",
					self.loadDatabase)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction("&Exit", self.close)
		self.menuBar().addMenu(self.fileMenu)

		self.dbMenu = QMenu("&Database", self)
		self.dbMenu.addAction("Manage &parts...",
				      self.manageParts)
		self.dbMenu.addAction("Manage &footprints...",
				      self.manageFootprints)
		self.dbMenu.addAction("Manage &locations...",
				      self.manageLocations)
		self.dbMenu.addAction("Manage &suppliers...",
				      self.manageSuppliers)
		self.dbMenu.addSeparator()
		self.dbMenu.addAction("Global &parameters...",
				      self.manageGlobalParams)
		self.menuBar().addMenu(self.dbMenu)

		self.statMenu = QMenu("&Statistics", self)
		self.statMenu.addAction("Show parts to &order...",
					self.showPartsToOrder)
		self.statMenu.addAction("Show global statistics...",
					self.showGlobalStats)
		self.menuBar().addMenu(self.statMenu)

		self.__enableDbMenus(False)
		self.updateTitle()

	def __enableDbMenus(self, enabled):
		self.dbMenu.setEnabled(enabled)
		self.statMenu.setEnabled(enabled)

	def updateTitle(self, filename=None):
		title = "Part manager"
		if filename:
			title += " - " + filename
		self.setWindowTitle(title)

	def showGlobalStats(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.showGlobalStats()

	def showPartsToOrder(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.showPartsToOrder()

	def manageGlobalParams(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.manageGlobalParams()

	def manageParts(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.manageParts()

	def manageFootprints(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.manageFootprints()

	def manageLocations(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.manageLocations()

	def manageSuppliers(self):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.manageSuppliers()

	def loadDatabase(self):
		fn, ok = QFileDialog.getSaveFileName(self,
				"Load database", "",
				"PartMgr files (*.pmg);;"
				"All files (*)",
				"", QFileDialog.DontConfirmOverwrite |
				QFileDialog.DontUseNativeDialog)
		if ok and fn:
			self.loadDatabaseFile(fn)

	def loadDatabaseFile(self, filename):
		try:
			db = Database(filename)
			self.setCentralWidget(PartMgrMainWidget(db, self))
		except PartMgrError as e:
			QMessageBox.critical(self, "Failed to load database",
					     str(e))
			return False
		self.__enableDbMenus(True)
		self.updateTitle(filename)
		return True

	def closeEvent(self, e):
		mainWidget = self.centralWidget()
		if mainWidget:
			mainWidget.shutdown()
			mainWidget.deleteLater()
			self.setCentralWidget(None)
