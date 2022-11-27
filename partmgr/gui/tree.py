# -*- coding: utf-8 -*-
#
# PartMgr GUI - Tree widget
#
# Copyright 2014-2022 Michael Buesch <m@bues.ch>
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
from partmgr.core.part import *


class TreeItem:
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
			return Qt.ItemFlag.NoItemFlags
		return Qt.ItemFlag.ItemIsEnabled |\
		       Qt.ItemFlag.ItemIsSelectable |\
		       Qt.ItemFlag.ItemIsEditable

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

	def data(self, index, role=Qt.ItemDataRole.DisplayRole):
		if not index.isValid():
			return None
		treeItem = self.modelIndexToTreeItem(index)
		if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
			entity = treeItem.toEntity(self.db)
			return entity.getName()
		elif role == Qt.ItemDataRole.DecorationRole:
			if treeItem.entityType == TreeItem.CATEGORY:
				icon = self.fileIconProv.icon(
					QFileIconProvider.IconType.Folder)
			else:
				icon = self.fileIconProv.icon(
					QFileIconProvider.IconType.File)
			return icon
		return None

	def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
		if not index.isValid():
			return False
		if role != Qt.ItemDataRole.EditRole:
			return False
		treeItem = self.modelIndexToTreeItem(index)
		self.renameTreeItem(treeItem, value)
		return QAbstractItemModel.setData(self, index, value, role)

	def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
		if role == Qt.ItemDataRole.DisplayRole:
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
		oldName = entity.getName()
		if newName == oldName:
			return

		# Set the new entity name.
		entity.setName(newName)

		if treeItem.entityType == TreeItem.STOCKITEM:
			stockItem = entity

			# Wheeeee, magic happens:
			# If a part is assigned to the stock item and we are
			# the only user of that part and the part has the same name,
			# the part is renamed, too.
			# If there was no old name and no part, we try to make a part
			# for this stock item, but only if the part does not exist.
			# If there is a part by that name, we take that.
			# Otherwise no part is assigned.

			db = stockItem.getDatabase()
			part = stockItem.getPart()
			category = stockItem.getCategory()
			allStockItems = db.getStockItemsByCategory(category)\
					if category else ()
			allParts = db.getPartsByCategory(category)\
				   if category else ()
			itemsWithSamePart = [ si for si in allStockItems
					      if si.getPart() == part ]
			partsWithNewName = [ p for p in allParts\
					     if p.getName() == newName ]

			if part and\
			   len(itemsWithSamePart) == 1 and\
			   itemsWithSamePart[0] == stockItem and\
			   part.getName().strip() == oldName.strip():
				# Also rename the part.
				part.setName(newName)
			elif not part and len(partsWithNewName) == 1:
				# Take this part which already has the new name.
				stockItem.setPart(partsWithNewName[0])
			elif not part and not oldName.strip():
				# Create a new part.
				newPart = Part(newName, category = category)
				db.modifyPart(newPart)
				stockItem.setPart(newPart)

		# Our data changed. Emit the signal.
		modelIndex = self.entityToModelIndex(entity)
		self.dataChanged.emit(modelIndex, modelIndex)

class Tree(QTreeView):
	itemChanged = Signal(int)

	def __init__(self, db, parent=None):
		QTreeView.__init__(self, parent)
		self.db = db

		model = TreeModel(db, self)
		proxyModel = QSortFilterProxyModel(self)
		proxyModel.setSourceModel(model)

		model.dataChanged.connect(self.__modelDataChanged)

		self.setModel(proxyModel)
		self.setSortingEnabled(True)
		self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

	def __modelDataChanged(self):
		selected = self.model().mapToSource(self.currentIndex())
		treeItem = self.realModel().modelIndexToTreeItem(selected)
		self.itemChanged.emit(treeItem.entityId)

	def realModel(self):
		return self.model().sourceModel()

	def currentChanged(self, selected, deselected):
		QTreeView.currentChanged(self, selected, deselected)
		if selected.isValid():
			selected = self.model().mapToSource(selected)
			treeItem = self.realModel().modelIndexToTreeItem(selected)
			if treeItem.entityType == TreeItem.STOCKITEM:
				self.itemChanged.emit(treeItem.entityId)
			else:
				self.itemChanged.emit(None)

	def contextMenuEvent(self, event):
		index = self.indexAt(event.pos())
		index = self.model().mapToSource(index)
		treeItem = self.realModel().modelIndexToTreeItem(index)
		self.contextTreeItem = treeItem
		menu = QMenu(self)
		if treeItem:
			if treeItem.entityType == TreeItem.CATEGORY:
				menu.addAction("Add sub-&category...",
					       self.addCategory)
				menu.addAction("Add &stock item...",
					       self.addStockItem)
				menu.addSeparator()
				menu.addAction("&Rename category",
					       self.renameCategory)
				menu.addAction("&Delete category",
					       self.delCategory)
			elif treeItem.entityType == TreeItem.STOCKITEM:
				menu.addAction("R&ename stock item",
					       self.renameStockItem)
				menu.addAction("De&lete stock item",
					       self.delStockItem)
			else:
				assert(0)
		else:
			menu.addAction("Add &root-category...", self.addCategory)
		menu.addSeparator()
		menu.addAction("Colla&pse all", self.collapseAll)
		menu.addAction("E&xpand all", self.expandAll)
		menu.exec(event.globalPos())
		super(Tree, self).contextMenuEvent(event)

	def keyPressEvent(self, ev):
		super(Tree, self).keyPressEvent(ev)

		if ev.key() == Qt.Key.Key_Delete:
			index = self.model().mapToSource(self.currentIndex())
			self.contextTreeItem = self.realModel().modelIndexToTreeItem(index)
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
		newModelIndex = self.realModel().addCategory(
					parentTreeItem, category)

		newModelIndex = self.model().mapFromSource(newModelIndex)
		if parentTreeItem:
			self.expand(self.model().mapFromSource(parentTreeItem.modelIndex))
		self.setCurrentIndex(newModelIndex)
		self.edit(newModelIndex)

	def delCategory(self):
		assert(self.contextTreeItem.entityType == TreeItem.CATEGORY)
		category = self.contextTreeItem.toEntity(self.db)
		ret = QMessageBox.question(self,
			"Really delete category?",
			"Really delete category '%s'?" % category.getName(),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if ret & QMessageBox.StandardButton.Yes == 0:
			return
		self.realModel().delTreeItem(self.contextTreeItem)

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
		self.realModel().renameTreeItem(self.contextTreeItem, newName)

	def renameStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.STOCKITEM)
		stockItem = self.contextTreeItem.toEntity(self.db)
		newName, ok = QInputDialog.getText(
				self, "Rename item",
				"Rename item",
				QLineEdit.Normal,
				stockItem.getName())
		if not ok:
			return
		self.realModel().renameTreeItem(self.contextTreeItem, newName)

	def addStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.CATEGORY)
		stockItem = StockItem("")
		newModelIndex = self.realModel().addStockItem(
					self.contextTreeItem, stockItem)
		newModelIndex = self.model().mapFromSource(newModelIndex)

		self.expand(self.model().mapFromSource(self.contextTreeItem.modelIndex))
		self.setCurrentIndex(newModelIndex)
		self.edit(newModelIndex)

	def delStockItem(self):
		assert(self.contextTreeItem.entityType == TreeItem.STOCKITEM)
		stockItem = self.contextTreeItem.toEntity(self.db)
		ret = QMessageBox.question(self,
			"Really delete item?",
			"Really delete item '%s'?" %\
			stockItem.getName(),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if ret & QMessageBox.StandardButton.Yes == 0:
			return
		self.realModel().delTreeItem(self.contextTreeItem)
