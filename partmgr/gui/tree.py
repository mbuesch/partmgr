# -*- coding: utf-8 -*-
#
# PartMgr GUI - Tree widget
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

from partmgr.gui.util import *

from partmgr.core.category import *
from partmgr.core.stockitem import *


class TreeItem(object):
	# Types
	CATEGORY	= 0
	STOCKITEM	= 1

	def __init__(self, entityType, entityId, modelIndex=None):
		self.entityType = entityType	# CATEGORY or STOCKITEM
		self.entityId = entityId	# Entity.id
		self.modelIndex = modelIndex

	def toEntity(self, db):
		if self.entityType == self.CATEGORY:
			return db.getCategory(self.entityId)
		elif self.entityType == self.STOCKITEM:
			return db.getStockItem(self.entityId)
		else:
			assert(0)

class TreeModel(QAbstractItemModel):
	def __init__(self, db, parent=None):
		QAbstractItemModel.__init__(self, parent)
		self.db = db

		self.fileIconProv = QFileIconProvider()

		self.__clearLookup()

	def __clearLookup(self):
		self.__idCount = 0
		self.__fwdLookup = {}
		self.__bwdLookup = {}

	def __treeItemToUniqueId(self, treeItem):
		key = (treeItem.entityType, treeItem.entityId)
		try:
			return self.__fwdLookup[key]
		except KeyError as e:
			newId = self.__idCount
			self.__idCount += 1
			self.__fwdLookup[key] = newId
			self.__bwdLookup[newId] = key
			return newId

	def __uniqueIdToTreeItem(self, uid):
		try:
			entityType, entityId = self.__bwdLookup[uid]
			return TreeItem(entityType, entityId)
		except KeyError as e:
			return None

	def __makeModelIndex(self, row, column, entity):
		if isinstance(entity, Category):
			entityType = TreeItem.CATEGORY
		elif isinstance(entity, StockItem):
			entityType = TreeItem.STOCKITEM
		else:
			assert(0)
		treeItem = TreeItem(entityType, entity.getId())
		uid = self.__treeItemToUniqueId(treeItem)
		return self.createIndex(row, column, int(uid))

	def entityToRowNumber(self, entity):
		parentCategory = entity.getParent()
		if not parentCategory:
			# entity is a root category.
			return self.db.getRootCategories().index(entity)
		if isinstance(entity, Category):
			return parentCategory.getChildCategories().index(entity)
		elif isinstance(entity, StockItem):
			return parentCategory.countChildCategories() +\
			       parentCategory.getChildStockItems().index(entity)
		assert(0)

	def entityToModelIndex(self, entity):
		if not entity:
			return QModelIndex()
		return self.__makeModelIndex(self.entityToRowNumber(entity),
					     0, entity)

	def modelIndexToTreeItem(self, modelIndex):
		if not modelIndex.isValid():
			return None
		uid = int(modelIndex.internalId())
		treeItem = self.__uniqueIdToTreeItem(uid)
		treeItem.modelIndex = modelIndex
		return treeItem

	def flags(self, index):
		if not index.isValid():
			return Qt.NoItemFlags
		return Qt.ItemIsEnabled |\
		       Qt.ItemIsSelectable |\
		       Qt.ItemIsEditable

	def columnCount(self, parentIndex=QModelIndex()):
		return 1

	def rowCount(self, parentIndex=QModelIndex()):
		if parentIndex.isValid():
			treeItem = self.modelIndexToTreeItem(parentIndex)
			if treeItem.entityType == TreeItem.CATEGORY:
				parentCatId = treeItem.entityId
				nrCats = self.db.countChildCategories(parentCatId)
				nrItems = self.db.countStockItemsByCategory(parentCatId)
				return nrCats + nrItems
		else:
			return self.db.countRootCategories()
		return 0

	def index(self, row, column, parentIndex=QModelIndex()):
		origRow, origColumn = row, column
		if row < 0 or column < 0:
			return QModelIndex()
		if parentIndex.isValid():
			treeItem = self.modelIndexToTreeItem(parentIndex)
			if treeItem.entityType != TreeItem.CATEGORY:
				return QModelIndex()
			parentCatId = treeItem.entityId
			childCats = self.db.getChildCategories(parentCatId)
			if row < len(childCats):
				return self.__makeModelIndex(origRow, origColumn,
							     childCats[row])
			row -= len(childCats)
			childItems = self.db.getStockItemsByCategory(parentCatId)
			if row < len(childItems):
				return self.__makeModelIndex(origRow, origColumn,
							     childItems[row])
			assert(0)
		else:
			cats = self.db.getRootCategories()
			if row < len(cats):
				return self.__makeModelIndex(origRow, origColumn,
							     cats[row])
		return QModelIndex()

	def parent(self, index):
		if not index.isValid():
			return QModelIndex()
		treeItem = self.modelIndexToTreeItem(index)
		if treeItem.entityType == TreeItem.CATEGORY:
			category = treeItem.toEntity(self.db)
			if not category:
				return QModelIndex()
			parentCat = category.getParent()
		elif treeItem.entityType == TreeItem.STOCKITEM:
			stockItem = treeItem.toEntity(self.db)
			if not stockItem:
				return QModelIndex()
			parentCat = stockItem.getCategory()
		else:
			assert(0)
		if parentCat is None:
			return QModelIndex()
		return self.entityToModelIndex(parentCat)

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return None
		treeItem = self.modelIndexToTreeItem(index)
		if role in (Qt.DisplayRole, Qt.EditRole):
			entity = treeItem.toEntity(self.db)
			return entity.getVerboseName()
		elif role == Qt.DecorationRole:
			if treeItem.entityType == TreeItem.CATEGORY:
				icon = self.fileIconProv.icon(
					QFileIconProvider.Folder)
			else:
				icon = self.fileIconProv.icon(
					QFileIconProvider.File)
			return icon
		return None

	def setData(self, index, value, role=Qt.EditRole):
		if not index.isValid():
			return False
		if role != Qt.EditRole:
			return False
		treeItem = self.modelIndexToTreeItem(index)
		entity = treeItem.toEntity(self.db)
		entity.setName(value)
		return QAbstractItemModel.setData(self, index, value, role)

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if role == Qt.DisplayRole:
			return "Stock items"
		return None

	# Add a new StockItem to the database
	def addStockItem(self, parentTreeItem, stockItem):
		assert(not stockItem.hasValidId() and\
		       not stockItem.hasCategory())
		parentCat = parentTreeItem.toEntity(self.db) if parentTreeItem\
			    else None
		stockItem.setCategory(parentCat) # reparent item
		self.db.modifyStockItem(stockItem) # Add it

		entityRow = self.entityToRowNumber(stockItem)
		self.rowsInserted.emit(self.entityToModelIndex(parentCat),
				       entityRow, entityRow)

		return self.entityToModelIndex(stockItem)

	# Add a new Category to the database
	def addCategory(self, parentTreeItem, category):
		assert(not category.hasValidId())
		parentCat = parentTreeItem.toEntity(self.db) if parentTreeItem\
			    else None
		category.setParent(parentCat) # reparent category
		self.db.modifyCategory(category) # Add it

		entityRow = self.entityToRowNumber(category)
		self.rowsInserted.emit(self.entityToModelIndex(parentCat),
				       entityRow, entityRow)

		return self.entityToModelIndex(category)

	# Delete a TreeItem (stock or category) from the database
	def delTreeItem(self, treeItem):
		if not treeItem:
			return
		entity = treeItem.toEntity(self.db)
		parentCat = entity.getParent()
		entityRow = self.entityToRowNumber(entity)
		entity.delete()

		self.rowsRemoved.emit(self.entityToModelIndex(parentCat),
				      entityRow, entityRow)

	# Rename a TreeItem (stock or category).
	def renameTreeItem(self, treeItem, newName):
		entity = treeItem.toEntity(self.db)
		entity.setName(newName)

		modelIndex = self.entityToModelIndex(entity)
		self.dataChanged.emit(modelIndex, modelIndex)

class Tree(QTreeView):
	itemChanged = Signal(int)

	def __init__(self, db, parent=None):
		QTreeView.__init__(self, parent)
		self.db = db
		self.setModel(TreeModel(db, self))

	def currentChanged(self, selected, deselected):
		QTreeView.currentChanged(self, selected, deselected)
		treeItem = self.model().modelIndexToTreeItem(selected)
		if treeItem.entityType == TreeItem.STOCKITEM:
			self.itemChanged.emit(treeItem.entityId)
		else:
			self.itemChanged.emit(None)

	def contextMenuEvent(self, event):
		treeItem = self.model().modelIndexToTreeItem(self.indexAt(event.pos()))
		self.contextTreeItem = treeItem
		menu = QMenu(self)
		if treeItem:
			if treeItem.entityType == TreeItem.CATEGORY:
				menu.addAction("Add sub-category...",
					       self.addCategory)
				menu.addAction("Add stock item...",
					       self.addStockItem)
				menu.addSeparator()
				menu.addAction("Rename category",
					       self.renameCategory)
				menu.addAction("Delete category",
					       self.delCategory)
			elif treeItem.entityType == TreeItem.STOCKITEM:
				menu.addAction("Rename stock item",
					       self.renameStockItem)
				menu.addAction("Delete stock item",
					       self.delStockItem)
			else:
				assert(0)
		else:
			menu.addAction("Add root-category...", self.addCategory)
		menu.exec_(event.globalPos())
		super(Tree, self).contextMenuEvent(event)

	def keyPressEvent(self, ev):
		super(Tree, self).keyPressEvent(ev)

		if ev.key() == Qt.Key_Delete:
			self.contextTreeItem = self.model().modelIndexToTreeItem(self.currentIndex())
			if not self.contextTreeItem:
				return
			if self.contextTreeItem.entityType == TreeItem.CATEGORY:
				self.delCategory()
			elif self.contextTreeItem.entityType == TreeItem.STOCKITEM:
				self.delStockItem()
			else:
				assert(0)

	def addCategory(self):
		parentTreeItem = self.contextTreeItem
		assert(parentTreeItem is None or\
		       parentTreeItem.entityType == TreeItem.CATEGORY)
		category = Category("New category")
		newModelIndex = self.model().addCategory(parentTreeItem,
							 category)

		if parentTreeItem:
			self.expand(parentTreeItem.modelIndex)
		self.setCurrentIndex(newModelIndex)
		self.edit(newModelIndex)


	def delCategory(self):
		assert(self.contextTreeItem.entityType == TreeItem.CATEGORY)
		category = self.contextTreeItem.toEntity(self.db)
		ret = QMessageBox.question(self,
			"Really delete category?",
			"Really delete category '%s'?" % category.getName(),
			QMessageBox.Yes | QMessageBox.No)
		if ret & QMessageBox.Yes == 0:
			return
		self.model().delTreeItem(self.contextTreeItem)

	def renameCategory(self):
		assert(self.contextTreeItem.entityType == TreeItem.CATEGORY)
		category = self.contextTreeItem.toEntity(self.db)
		newName, ok = QInputDialog.getText(
				self, "Rename category",
				"Rename category",
				QLineEdit.Normal,
				category.getName())
		if not ok:
			return
		self.model().renameTreeItem(self.contextTreeItem, newName)

	def renameStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.STOCKITEM)
		stockItem = self.contextTreeItem.toEntity(self.db)
		newName, ok = QInputDialog.getText(
				self, "Rename item",
				"Rename item",
				QLineEdit.Normal,
				stockItem.getVerboseName())
		if not ok:
			return
		self.model().renameTreeItem(self.contextTreeItem, newName)

	def addStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.CATEGORY)
		stockItem = StockItem("")
		newModelIndex = self.model().addStockItem(self.contextTreeItem,
							  stockItem)

		self.expand(self.contextTreeItem.modelIndex)
		self.setCurrentIndex(newModelIndex)
		self.edit(newModelIndex)

	def delStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.STOCKITEM)
		stockItem = self.contextTreeItem.toEntity(self.db)
		ret = QMessageBox.question(self,
			"Really delete item?",
			"Really delete item '%s'?" %\
			stockItem.getVerboseName(),
			QMessageBox.Yes | QMessageBox.No)
		if ret & QMessageBox.Yes == 0:
			return
		self.model().delTreeItem(self.contextTreeItem)
