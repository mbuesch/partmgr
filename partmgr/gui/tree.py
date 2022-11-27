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
from partmgr.core.entity import Entity_XmlFactory
from partmgr.core.xmlfactory import XmlFactory

import sys


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

	def supportedDropActions(self):
		return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

	def flags(self, index):
		if not index.isValid():
			return Qt.ItemFlag.NoItemFlags
		treeItem = self.modelIndexToTreeItem(index)
		flags = (Qt.ItemFlag.ItemIsEnabled |
			 Qt.ItemFlag.ItemIsSelectable |
			 Qt.ItemFlag.ItemIsEditable |
			 Qt.ItemFlag.ItemIsDragEnabled)
		if treeItem.entityType == TreeItem.CATEGORY:
			flags |= Qt.ItemFlag.ItemIsDropEnabled
		return flags

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

	def mimeData(self, indexes):
		if not indexes:
			return None
		mimeData = QMimeData()
		for index in indexes:
			if not index.isValid():
				continue
			treeItem = self.modelIndexToTreeItem(index)
			entity = treeItem.toEntity(self.db)
			if not entity:
				continue
			# Serialize the entity (including all of its
			# children, if it is a category) to XML.
			if treeItem.entityType == TreeItem.CATEGORY:
				dataBytes = Category_XmlFactory(
					entity=entity).compose()
				mimeData.setData("application/x-partmgr-xml-category",
						 dataBytes)
			elif treeItem.entityType == TreeItem.STOCKITEM:
				dataBytes = StockItem_XmlFactory(
					entity=entity).compose()
				mimeData.setData("application/x-partmgr-xml-stockitem",
						 dataBytes)
			else:
				assert False
		return mimeData

	def dropMimeData(self, mimeData, action, row, column, parentIndex):
		if self.__dropMimeData(mimeData, action, row, column, parentIndex):
			return True
		return False

	def mimeTypes(self):
		return [
			"application/x-partmgr-xml-category",
			"application/x-partmgr-xml-stockitem",
		]

	def canDropMimeData(self, mimeData, action, row, column, parentIndex):
		if not parentIndex.isValid():
			return False
		if action not in (Qt.DropAction.MoveAction,
				  Qt.DropAction.CopyAction):
			return False
		parentTreeItem = self.modelIndexToTreeItem(parentIndex)
		if parentTreeItem.entityType != TreeItem.CATEGORY:
			return False
		if mimeData.hasFormat("application/x-partmgr-xml-stockitem"):
			return True
		if mimeData.hasFormat("application/x-partmgr-xml-category"):
			if action == Qt.DropAction.MoveAction:
				# Reject moving a category into itself or
				# into one of its own child categories.
				draggedEntity = self.__parseDraggedEntity(mimeData)
				if draggedEntity is None or\
				   not draggedEntity.hasValidId():
					return False
				cat = parentTreeItem.toEntity(self.db)
				while cat:
					if cat.id == draggedEntity.id:
						return False
					cat = cat.getParent()
			return True
		return False

	def __parseDraggedEntity(self, mimeData):
		"""Parse the dragged entity from the drag&drop MIME data.
		Returns the (detached) entity, or None on error.
		"""
		if mimeData.hasFormat("application/x-partmgr-xml-category"):
			mimeType = "application/x-partmgr-xml-category"
			entityClass = Category
		elif mimeData.hasFormat("application/x-partmgr-xml-stockitem"):
			mimeType = "application/x-partmgr-xml-stockitem"
			entityClass = StockItem
		else:
			return None
		try:
			factory = Entity_XmlFactory()
			# QMimeData.data() -> QByteArray; .data() -> bytes
			xmlBytes = mimeData.data(mimeType).data()
			if not factory.parse(xmlBytes):
				return None
		except XmlFactory.Error as e:
			print("Failed to parse drag&drop XML data: %s" % str(e),
			      file=sys.stderr)
			return None
		entity = factory.entity
		if not isinstance(entity, entityClass):
			return None
		return entity

	def __dropMimeData(self, mimeData, action, row, column, parentIndex):
		if action not in (Qt.DropAction.MoveAction,
				  Qt.DropAction.CopyAction):
			return False
		if not parentIndex.isValid():
			return False
		parentTreeItem = self.modelIndexToTreeItem(parentIndex)
		if not parentTreeItem or\
		   parentTreeItem.entityType != TreeItem.CATEGORY:
			return False
		targetCategory = parentTreeItem.toEntity(self.db)
		if not targetCategory:
			return False

		# Deserialize the dragged entity from the XML MIME data.
		draggedEntity = self.__parseDraggedEntity(mimeData)
		if draggedEntity is None or not draggedEntity.hasValidId():
			return False

		if action == Qt.DropAction.MoveAction:
			return self.__dropMove(draggedEntity, targetCategory)
		# Qt.DropAction.CopyAction
		return self.__dropCopy(draggedEntity, parentTreeItem)

	def __dropMove(self, draggedEntity, targetCategory):
		"""Move an entity to another category.
		'draggedEntity' is the (detached) entity parsed from the
		drag&drop XML data. The actual database entity is fetched
		by its ID.
		"""
		# Get the actual entity from the database.
		if isinstance(draggedEntity, Category):
			entity = self.db.getCategory(draggedEntity.id)
		elif isinstance(draggedEntity, StockItem):
			entity = self.db.getStockItem(draggedEntity.id)
		else:
			assert False
		if not entity:
			return False

		if isinstance(entity, Category):
			# Do not move a category into itself or into
			# one of its own child categories.
			cat = targetCategory
			while cat:
				if cat == entity:
					return False
				cat = cat.getParent()

		oldParentCat = entity.getParent()
		if oldParentCat == targetCategory:
			# Already there. Nothing to do.
			return False

		# Move the model row and update the database.
		sourceParentIndex = self.entityToModelIndex(oldParentCat)
		sourceRow = self.entityToRowNumber(entity)
		destParentIndex = self.entityToModelIndex(targetCategory)
		destRow = self.rowCount(destParentIndex)
		if not self.beginMoveRows(sourceParentIndex,
					  sourceRow, sourceRow,
					  destParentIndex,
					  destRow):
			return False
		if isinstance(entity, Category):
			entity.setParent(targetCategory)
		else:
			self.__movePartWithStockItem(entity, targetCategory)
			entity.setCategory(targetCategory)
		self.endMoveRows()
		return True

	def __movePartWithStockItem(self, stockItem, targetCategory):
		"""A StockItem is being moved to targetCategory. Take the
		Part it refers to along, so it stays reachable from the
		stock item's new category:
		If an identical part already exists in targetCategory, it is
		reused. Otherwise, if the part is only used by this one
		stock item, the part is moved to targetCategory, too. If the
		part is shared with other stock items, it is duplicated
		instead, so that the other stock items keep referring to the
		original, unmodified part.
		"""
		part = stockItem.getPart()
		if not part:
			return
		existingPart = self.__findMatchingPart(part, targetCategory)
		if existingPart:
			stockItem.setPart(existingPart)
		elif len(self.db.getStockItemsByPart(part)) <= 1:
			part.setCategory(targetCategory)
		else:
			stockItem.setPart(self.__duplicatePart(part, targetCategory))

	def __findMatchingPart(self, part, targetCategory):
		"""Find a Part in targetCategory that is identical to 'part'
		(same name, description and flags). Returns the matching
		Part, or None if there is no such part.
		"""
		for candidate in self.db.getPartsByCategory(targetCategory):
			if candidate.id == part.id:
				continue
			if (candidate.name.strip() == part.name.strip() and
			    candidate.description.strip() == part.description.strip() and
			    candidate.flags == part.flags):
				return candidate
		return None

	def __duplicatePart(self, srcPart, targetCategory):
		"""Duplicate a Part into targetCategory. If an identical part
		already exists in targetCategory, that existing part is
		reused instead of creating a duplicate. Returns the new or
		reused Part.
		"""
		existingPart = self.__findMatchingPart(srcPart, targetCategory)
		if existingPart:
			return existingPart
		newPart = Part(
			name=srcPart.name,
			description=srcPart.description,
			flags=srcPart.flags,
			category=targetCategory,
		)
		self.db.modifyPart(newPart)
		return newPart

	def __dropCopy(self, draggedEntity, parentTreeItem):
		"""Copy an entity into another category.
		The entity (including all of its content, if it is a
		category) is duplicated with new database IDs.
		"""
		if isinstance(draggedEntity, Category):
			self.__copyCategory(draggedEntity, parentTreeItem)
		elif isinstance(draggedEntity, StockItem):
			self.__copyStockItem(draggedEntity, parentTreeItem)
		else:
			assert False
		return True

	def __copyCategory(self, srcCategory, parentTreeItem):
		"""Recursively copy a category and all of its content.
		'srcCategory' is the (detached) category parsed from the
		drag&drop XML data.
		"""
		newCategory = Category(
			name=srcCategory.name,
			description=srcCategory.description,
			flags=srcCategory.flags,
		)
		newIndex = self.addCategory(parentTreeItem, newCategory)
		newTreeItem = self.modelIndexToTreeItem(newIndex)
		for childCategory in getattr(srcCategory, "childCategories", ()):
			self.__copyCategory(childCategory, newTreeItem)
		for childStockItem in getattr(srcCategory, "childStockItems", ()):
			self.__copyStockItem(childStockItem, newTreeItem)

	def __copyStockItem(self, srcStockItem, parentTreeItem):
		"""Copy a stock item.
		The new stock item refers to a copy of the part (if any),
		and to the same footprint, but it has no storages or origins.
		'srcStockItem' is the (detached) stock item parsed from the
		drag&drop XML data.
		"""
		targetCategory = parentTreeItem.toEntity(self.db)
		srcPart = self.db.getPart(srcStockItem.part)
		newPart = self.__duplicatePart(srcPart, targetCategory) if srcPart else None
		newStockItem = StockItem(
			name=srcStockItem.name,
			description=srcStockItem.description,
			flags=srcStockItem.flags,
			part=newPart,
			footprint=srcStockItem.footprint,
			minQuantity=srcStockItem.minQuantity,
			targetQuantity=srcStockItem.targetQuantity,
			quantityUnits=srcStockItem.quantityUnits,
		)
		self.addStockItem(parentTreeItem, newStockItem)

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

		self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
		self.setDefaultDropAction(Qt.DropAction.MoveAction)
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.setDropIndicatorShown(True)
		self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

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
				QLineEdit.EchoMode.Normal,
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
				QLineEdit.EchoMode.Normal,
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
