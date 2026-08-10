#
# PartMgr - Unit tests for tree drag&drop (XML serialization)
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

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import tempfile

from partmgr_tstlib import *

from partmgr.core.database import *
from partmgr.core.entity import Entity, Entity_XmlFactory, EntityList_XmlFactory
from partmgr.core.category import Category, Category_XmlFactory
from partmgr.core.stockitem import StockItem, StockItem_XmlFactory
from partmgr.core.part import Part
from partmgr.core.xmlfactory import XmlFactory


class TestCaseContext:
	"""Test context: A temporary database with a category tree.

	Tree structure:
	    RootA (multiline+unicode description)
	      +- SubB
	      |    +- ItemB1
	      +- ItemA1
	    RootC (empty)
	"""

	def __enter__(self):
		self.__tmp = tempfile.TemporaryDirectory(prefix="partmgr-test-")
		dbFile = os.path.join(self.__tmp.name, "test.pmg")
		self.db = Database(dbFile)
		db = self.db

		self.rootA = Category("RootA",
			description="First line\nSecond line\nUnicode: äöüµ€",
			flags=42)
		db.modifyCategory(self.rootA)

		self.subB = Category("SubB", parent=self.rootA)
		db.modifyCategory(self.subB)

		self.rootC = Category("RootC")
		db.modifyCategory(self.rootC)

		self.itemA1 = StockItem("ItemA1",
			category=self.rootA,
			description="Item\nA1",
			flags=7,
			minQuantity=3,
			targetQuantity=5,
			quantityUnits=StockItem.UNIT_MM)
		db.modifyStockItem(self.itemA1)

		self.itemB1 = StockItem("ItemB1",
			category=self.subB,
			minQuantity=0,
			targetQuantity=1,
			quantityUnits=StockItem.UNIT_L)
		db.modifyStockItem(self.itemB1)

		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		self.db.close()
		self.__tmp.cleanup()


class Test_DndXml(TestCase):
	def test_categoryXmlRoundtrip(self):
		with TestCaseContext() as ctx:
			cat = ctx.db.getCategory(ctx.rootA.id)

			# Compose the category (with all children) to XML.
			xmlBytes = Category_XmlFactory(entity=cat).compose()
			xmlStr = xmlBytes.decode(XmlFactory.XML_ENCODING)
			print("--- Category XML ---")
			print(xmlStr)
			print("--------------------")
			self.assertIn('entityType="category"', xmlStr)
			self.assertIn("<categories>", xmlStr)
			self.assertIn("<stockitems>", xmlStr)

			# Parse the XML back into an entity tree.
			factory = Entity_XmlFactory()
			self.assertTrue(factory.parse(xmlBytes))
			parsed = factory.entity
			self.assertIsNotNone(parsed)
			self.assertIsInstance(parsed, Category)
			self.assertEqual(parsed.id, cat.id)
			self.assertEqual(parsed.name, cat.name)
			self.assertEqual(parsed.description, cat.description)
			self.assertEqual(parsed.flags, cat.flags)
			self.assertEqual(parsed.parent, cat.parent)
			self.assertEqual(parsed.createTimeStamp.getStampInt(),
					 cat.createTimeStamp.getStampInt())
			self.assertEqual(parsed.modifyTimeStamp.getStampInt(),
					 cat.modifyTimeStamp.getStampInt())

			# Check the child categories.
			self.assertEqual(len(parsed.childCategories), 1)
			parsedSubB = parsed.childCategories[0]
			self.assertIsInstance(parsedSubB, Category)
			self.assertEqual(parsedSubB.id, ctx.subB.id)
			self.assertEqual(parsedSubB.name, "SubB")
			self.assertEqual(parsedSubB.parent, ctx.rootA.id)
			# SubB has no child categories, but one stock item.
			self.assertEqual(len(parsedSubB.childCategories), 0)
			self.assertEqual(len(parsedSubB.childStockItems), 1)
			parsedItemB1 = parsedSubB.childStockItems[0]
			self.assertIsInstance(parsedItemB1, StockItem)
			self.assertEqual(parsedItemB1.id, ctx.itemB1.id)
			self.assertEqual(parsedItemB1.name, "ItemB1")
			self.assertEqual(parsedItemB1.category, ctx.subB.id)
			self.assertEqual(parsedItemB1.targetQuantity, 1)
			self.assertEqual(parsedItemB1.quantityUnits, StockItem.UNIT_L)

			# Check the child stock items of RootA.
			self.assertEqual(len(parsed.childStockItems), 1)
			parsedItemA1 = parsed.childStockItems[0]
			self.assertIsInstance(parsedItemA1, StockItem)
			self.assertEqual(parsedItemA1.id, ctx.itemA1.id)
			self.assertEqual(parsedItemA1.name, "ItemA1")
			self.assertEqual(parsedItemA1.description, "Item\nA1")
			self.assertEqual(parsedItemA1.flags, 7)
			self.assertEqual(parsedItemA1.category, ctx.rootA.id)
			self.assertEqual(parsedItemA1.part, Entity.NO_ID)
			self.assertEqual(parsedItemA1.footprint, Entity.NO_ID)
			self.assertEqual(parsedItemA1.minQuantity, 3)
			self.assertEqual(parsedItemA1.targetQuantity, 5)
			self.assertEqual(parsedItemA1.quantityUnits, StockItem.UNIT_MM)

	def test_stockItemXmlRoundtrip(self):
		with TestCaseContext() as ctx:
			item = ctx.db.getStockItem(ctx.itemA1.id)

			xmlBytes = StockItem_XmlFactory(entity=item).compose()
			xmlStr = xmlBytes.decode(XmlFactory.XML_ENCODING)
			print("--- StockItem XML ---")
			print(xmlStr)
			print("---------------------")
			self.assertIn('entityType="stockitem"', xmlStr)

			factory = Entity_XmlFactory()
			self.assertTrue(factory.parse(xmlBytes))
			parsed = factory.entity
			self.assertIsNotNone(parsed)
			self.assertIsInstance(parsed, StockItem)
			self.assertEqual(parsed.id, item.id)
			self.assertEqual(parsed.name, item.name)
			self.assertEqual(parsed.description, item.description)
			self.assertEqual(parsed.flags, item.flags)
			self.assertEqual(parsed.category, item.category)
			self.assertEqual(parsed.part, item.part)
			self.assertEqual(parsed.footprint, item.footprint)
			self.assertEqual(parsed.minQuantity, item.minQuantity)
			self.assertEqual(parsed.targetQuantity, item.targetQuantity)
			self.assertEqual(parsed.quantityUnits, item.quantityUnits)
			self.assertEqual(parsed.createTimeStamp.getStampInt(),
					 item.createTimeStamp.getStampInt())
			self.assertEqual(parsed.modifyTimeStamp.getStampInt(),
					 item.modifyTimeStamp.getStampInt())

	def test_parseErrors(self):
		factory = Entity_XmlFactory()
		# Empty input is not an error, but yields no entity.
		self.assertFalse(factory.parse(b""))
		self.assertIsNone(factory.entity)
		# Garbage input raises an XmlFactory.Error.
		factory = Entity_XmlFactory()
		self.assertRaises(XmlFactory.Error,
				  factory.parse, b"this is < not XML")
		# Unknown entityType raises an XmlFactory.Error.
		factory = Entity_XmlFactory()
		self.assertRaises(XmlFactory.Error, factory.parse,
			b'<entity entityType="unknown" id="1" name="" description="" '
			b'flags="0" createTimeStamp="1" modifyTimeStamp="1" />')


class Test_DndTreeModel(TestCase):
	"""Test the TreeModel drag&drop logic.
	This does not open any GUI. It only exercises the model code.
	"""

	@classmethod
	def setUpClass(cls):
		from partmgr.qt_bindings import QApplication
		cls.app = QApplication.instance() or QApplication([])

	def setUp(self):
		from partmgr.gui.tree import TreeModel
		self.ctx = TestCaseContext()
		self.ctx.__enter__()
		self.model = TreeModel(self.ctx.db)

	def tearDown(self):
		self.ctx.__exit__(None, None, None)

	def __entityIndex(self, entity):
		index = self.model.entityToModelIndex(entity)
		self.assertTrue(index.isValid())
		return index

	def __makeMimeData(self, entity):
		index = self.__entityIndex(entity)
		mimeData = self.model.mimeData([ index ])
		self.assertIsNotNone(mimeData)
		return mimeData

	def __canDrop(self, mimeData, action, targetEntity):
		parentIndex = self.__entityIndex(targetEntity)
		return self.model.canDropMimeData(
			mimeData, action, -1, -1, parentIndex)

	def __drop(self, mimeData, action, targetEntity):
		parentIndex = self.__entityIndex(targetEntity)
		return self.model.dropMimeData(
			mimeData, action, -1, -1, parentIndex)

	def test_mimeData(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		mimeData = self.__makeMimeData(ctx.rootA)
		self.assertTrue(mimeData.hasFormat("application/x-partmgr-xml-category"))
		xmlBytes = mimeData.data("application/x-partmgr-xml-category").data()
		factory = Entity_XmlFactory()
		self.assertTrue(factory.parse(xmlBytes))
		self.assertIsInstance(factory.entity, Category)
		self.assertEqual(factory.entity.id, ctx.rootA.id)
		self.assertEqual(len(factory.entity.childCategories), 1)
		self.assertEqual(len(factory.entity.childStockItems), 1)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(mimeData.hasFormat("application/x-partmgr-xml-stockitem"))
		xmlBytes = mimeData.data("application/x-partmgr-xml-stockitem").data()
		factory = Entity_XmlFactory()
		self.assertTrue(factory.parse(xmlBytes))
		self.assertIsInstance(factory.entity, StockItem)
		self.assertEqual(factory.entity.id, ctx.itemA1.id)

	def test_canDrop(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx
		Move = Qt.DropAction.MoveAction
		Copy = Qt.DropAction.CopyAction

		catMime = self.__makeMimeData(ctx.rootA)
		stockMime = self.__makeMimeData(ctx.itemA1)

		# Dropping onto a category is ok.
		self.assertTrue(self.__canDrop(catMime, Copy, ctx.rootC))
		self.assertTrue(self.__canDrop(stockMime, Copy, ctx.rootC))
		self.assertTrue(self.__canDrop(stockMime, Move, ctx.rootC))

		# Moving a category into itself or a child is forbidden.
		self.assertFalse(self.__canDrop(catMime, Move, ctx.rootA))
		self.assertFalse(self.__canDrop(catMime, Move, ctx.subB))
		# ... but copying there is ok.
		self.assertTrue(self.__canDrop(catMime, Copy, ctx.rootA))

		# Dropping onto a stock item is forbidden.
		self.assertFalse(self.__canDrop(stockMime, Move, ctx.itemA1))

		# Unsupported actions are rejected.
		self.assertFalse(self.__canDrop(catMime, Qt.DropAction.IgnoreAction,
						ctx.rootC))
		self.assertFalse(self.__canDrop(catMime, Qt.DropAction.LinkAction,
						ctx.rootC))

		# Unknown MIME formats are rejected.
		from partmgr.gui.tree import QMimeData
		bogusMime = QMimeData()
		bogusMime.setData("text/plain", b"bogus")
		self.assertFalse(self.__canDrop(bogusMime, Move, ctx.rootC))

	def test_moveStockItem(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The item is now in RootC.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootC.id)
		self.assertEqual([ i.id for i in ctx.rootC.getChildStockItems() ],
				 [ ctx.itemA1.id ])
		self.assertEqual(ctx.db.getStockItemsByCategory(ctx.rootA), [])

	def test_moveStockItemNoop(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		# Moving an item into its own category is a no-op.
		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertFalse(self.__drop(mimeData, Qt.DropAction.MoveAction,
					     ctx.rootA))
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootA.id)

	def test_moveStockItem_exclusivePartMovesAlong(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartA1", category=ctx.rootA)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The item moved, and still refers to the very same part.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootC.id)
		self.assertEqual(item.part, part.id)

		# The part moved along, since it had no other users.
		movedPart = ctx.db.getPart(part.id)
		self.assertEqual(movedPart.category, ctx.rootC.id)
		self.assertEqual(len(ctx.db.getParts()), 1)

	def test_moveStockItem_exclusivePartReusesExistingMatch(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartA1", category=ctx.rootA, description="d", flags=5)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		# An identical part already exists in the target category.
		existing = Part("PartA1", category=ctx.rootC, description="d", flags=5)
		ctx.db.modifyPart(existing)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The item now refers to the existing matching part, not a new one.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootC.id)
		self.assertEqual(item.part, existing.id)

		# The original part was left behind, untouched.
		origPart = ctx.db.getPart(part.id)
		self.assertEqual(origPart.category, ctx.rootA.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_moveStockItem_similarButDifferentPartNotReused(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartA1", category=ctx.rootA, description="d", flags=5)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		# A same-named part exists in the target, but its description differs.
		other = Part("PartA1", category=ctx.rootC, description="different", flags=5)
		ctx.db.modifyPart(other)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The dissimilar part was not reused; the original part moved along.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.part, part.id)
		movedPart = ctx.db.getPart(part.id)
		self.assertEqual(movedPart.category, ctx.rootC.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_moveStockItem_sharedPartIsDuplicated(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("Shared", category=ctx.rootA, description="d", flags=9)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		# A second stock item in the same category uses the same part.
		itemA2 = StockItem("ItemA2", category=ctx.rootA)
		ctx.db.modifyStockItem(itemA2)
		itemA2.setPart(part)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The moved item now refers to a new, duplicated part in RootC.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootC.id)
		self.assertNotEqual(item.part, part.id)
		newPart = ctx.db.getPart(item.part)
		self.assertIsNotNone(newPart)
		self.assertEqual(newPart.name, "Shared")
		self.assertEqual(newPart.description, "d")
		self.assertEqual(newPart.flags, 9)
		self.assertEqual(newPart.category, ctx.rootC.id)

		# The original part is unchanged and still used by ItemA2.
		origPart = ctx.db.getPart(part.id)
		self.assertEqual(origPart.category, ctx.rootA.id)
		itemA2 = ctx.db.getStockItem(itemA2.id)
		self.assertEqual(itemA2.part, part.id)
		self.assertEqual(itemA2.category, ctx.rootA.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_moveStockItem_sharedPartReusesExistingMatch(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("Shared", category=ctx.rootA, description="d", flags=9)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		# A second stock item in the same category uses the same part.
		itemA2 = StockItem("ItemA2", category=ctx.rootA)
		ctx.db.modifyStockItem(itemA2)
		itemA2.setPart(part)

		# An identical part already exists in the target category.
		existing = Part("Shared", category=ctx.rootC, description="d", flags=9)
		ctx.db.modifyPart(existing)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# The moved item refers to the existing matching part, not a new copy.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootC.id)
		self.assertEqual(item.part, existing.id)

		# The original part is unchanged and still used by ItemA2.
		origPart = ctx.db.getPart(part.id)
		self.assertEqual(origPart.category, ctx.rootA.id)
		itemA2 = ctx.db.getStockItem(itemA2.id)
		self.assertEqual(itemA2.part, part.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_moveCategory(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		mimeData = self.__makeMimeData(ctx.subB)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))

		# SubB is now a child of RootC, with its stock item.
		subB = ctx.db.getCategory(ctx.subB.id)
		self.assertEqual(subB.parent, ctx.rootC.id)
		self.assertEqual([ c.id for c in ctx.rootC.getChildCategories() ],
				 [ ctx.subB.id ])
		self.assertEqual(ctx.db.getChildCategories(ctx.rootA), [])
		self.assertEqual([ i.id for i in subB.getChildStockItems() ],
				 [ ctx.itemB1.id ])

	def test_moveCategoryCycle(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		# Moving RootA into its own child SubB must fail.
		mimeData = self.__makeMimeData(ctx.rootA)
		self.assertFalse(self.__drop(mimeData, Qt.DropAction.MoveAction,
					     ctx.subB))
		rootA = ctx.db.getCategory(ctx.rootA.id)
		self.assertEqual(rootA.parent, Entity.NO_ID)
		# Moving RootA into itself must fail.
		mimeData = self.__makeMimeData(ctx.rootA)
		self.assertFalse(self.__drop(mimeData, Qt.DropAction.MoveAction,
					     ctx.rootA))
		rootA = ctx.db.getCategory(ctx.rootA.id)
		self.assertEqual(rootA.parent, Entity.NO_ID)

	def test_copyStockItem(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.CopyAction,
					    ctx.rootC))

		# The original item is unchanged.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootA.id)
		# There is a copy in RootC.
		copies = ctx.db.getStockItemsByCategory(ctx.rootC)
		self.assertEqual(len(copies), 1)
		copied = copies[0]
		self.assertNotEqual(copied.id, ctx.itemA1.id)
		self.assertEqual(copied.name, "ItemA1")
		self.assertEqual(copied.description, "Item\nA1")
		self.assertEqual(copied.flags, 7)
		self.assertEqual(copied.minQuantity, 3)
		self.assertEqual(copied.targetQuantity, 5)
		self.assertEqual(copied.quantityUnits, StockItem.UNIT_MM)

	def test_copyStockItem_partIsCopied(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartA1", category=ctx.rootA, description="d", flags=5)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.CopyAction,
					    ctx.rootC))

		# The original item and part are unchanged.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.category, ctx.rootA.id)
		self.assertEqual(item.part, part.id)

		# The copy refers to a new, independent copy of the part.
		copies = ctx.db.getStockItemsByCategory(ctx.rootC)
		self.assertEqual(len(copies), 1)
		copied = copies[0]
		self.assertNotEqual(copied.part, part.id)
		copiedPart = ctx.db.getPart(copied.part)
		self.assertIsNotNone(copiedPart)
		self.assertEqual(copiedPart.name, "PartA1")
		self.assertEqual(copiedPart.description, "d")
		self.assertEqual(copiedPart.flags, 5)
		self.assertEqual(copiedPart.category, ctx.rootC.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_copyStockItem_reusesExistingMatchingPart(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartA1", category=ctx.rootA, description="d", flags=5)
		ctx.db.modifyPart(part)
		ctx.itemA1.setPart(part)

		# An identical part already exists in the target category.
		existing = Part("PartA1", category=ctx.rootC, description="d", flags=5)
		ctx.db.modifyPart(existing)

		mimeData = self.__makeMimeData(ctx.itemA1)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.CopyAction,
					    ctx.rootC))

		# The original item and part are unchanged.
		item = ctx.db.getStockItem(ctx.itemA1.id)
		self.assertEqual(item.part, part.id)

		# The copy refers to the existing matching part, not a new one.
		copies = ctx.db.getStockItemsByCategory(ctx.rootC)
		self.assertEqual(len(copies), 1)
		copied = copies[0]
		self.assertEqual(copied.part, existing.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_copyCategoryRecursive(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		mimeData = self.__makeMimeData(ctx.rootA)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.CopyAction,
					    ctx.rootC))

		# The original tree is unchanged.
		rootA = ctx.db.getCategory(ctx.rootA.id)
		self.assertEqual(rootA.parent, Entity.NO_ID)
		self.assertEqual([ c.id for c in rootA.getChildCategories() ],
				 [ ctx.subB.id ])
		self.assertEqual([ i.id for i in rootA.getChildStockItems() ],
				 [ ctx.itemA1.id ])

		# RootC has a copy of the whole RootA subtree.
		copiedCats = ctx.db.getChildCategories(ctx.rootC)
		self.assertEqual(len(copiedCats), 1)
		copiedA = copiedCats[0]
		self.assertNotEqual(copiedA.id, ctx.rootA.id)
		self.assertEqual(copiedA.name, "RootA")
		self.assertEqual(copiedA.description, rootA.description)
		self.assertEqual(copiedA.flags, 42)

		# The copied category has a copy of SubB ...
		copiedSubCats = ctx.db.getChildCategories(copiedA)
		self.assertEqual(len(copiedSubCats), 1)
		copiedSubB = copiedSubCats[0]
		self.assertNotEqual(copiedSubB.id, ctx.subB.id)
		self.assertEqual(copiedSubB.name, "SubB")
		# ... with a copy of ItemB1 ...
		copiedBItems = ctx.db.getStockItemsByCategory(copiedSubB)
		self.assertEqual(len(copiedBItems), 1)
		copiedItemB1 = copiedBItems[0]
		self.assertNotEqual(copiedItemB1.id, ctx.itemB1.id)
		self.assertEqual(copiedItemB1.name, "ItemB1")
		self.assertEqual(copiedItemB1.quantityUnits, StockItem.UNIT_L)
		# ... and a copy of ItemA1 directly under copied RootA.
		copiedAItems = ctx.db.getStockItemsByCategory(copiedA)
		self.assertEqual(len(copiedAItems), 1)
		copiedItemA1 = copiedAItems[0]
		self.assertNotEqual(copiedItemA1.id, ctx.itemA1.id)
		self.assertEqual(copiedItemA1.name, "ItemA1")

	def test_copyCategoryRecursive_partIsCopied(self):
		from partmgr.gui.tree import Qt
		ctx = self.ctx

		part = Part("PartB1", category=ctx.subB)
		ctx.db.modifyPart(part)
		ctx.itemB1.setPart(part)

		mimeData = self.__makeMimeData(ctx.rootA)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.CopyAction,
					    ctx.rootC))

		# The original part is unchanged.
		origPart = ctx.db.getPart(part.id)
		self.assertEqual(origPart.category, ctx.subB.id)

		# The copied ItemB1 (nested two levels down) refers to its own
		# copy of the part, placed in the copied SubB category.
		copiedA = ctx.db.getChildCategories(ctx.rootC)[0]
		copiedSubB = ctx.db.getChildCategories(copiedA)[0]
		copiedItemB1 = ctx.db.getStockItemsByCategory(copiedSubB)[0]
		self.assertNotEqual(copiedItemB1.part, part.id)
		copiedPart = ctx.db.getPart(copiedItemB1.part)
		self.assertIsNotNone(copiedPart)
		self.assertEqual(copiedPart.name, "PartB1")
		self.assertEqual(copiedPart.category, copiedSubB.id)

		self.assertEqual(len(ctx.db.getParts()), 2)

	def test_treeModelConsistency(self):
		from partmgr.gui.tree import Qt, TreeItem
		ctx = self.ctx

		# Check the model content before the move.
		def checkTree():
			self.assertEqual(self.model.rowCount(), 2)
			idxA = self.model.index(0, 0)
			idxC = self.model.index(1, 0)
			self.assertTrue(idxA.isValid())
			self.assertTrue(idxC.isValid())
			itemA = self.model.modelIndexToTreeItem(idxA)
			itemC = self.model.modelIndexToTreeItem(idxC)
			self.assertEqual(itemA.entityId, ctx.rootA.id)
			self.assertEqual(itemC.entityId, ctx.rootC.id)
			self.assertEqual(self.model.rowCount(idxA), 2)
			self.assertEqual(self.model.rowCount(idxC), 0)
			idxB = self.model.index(0, 0, idxA)
			self.assertEqual(self.model.modelIndexToTreeItem(idxB).entityId,
					 ctx.subB.id)
			self.assertEqual(self.model.rowCount(idxB), 1)
			return idxA, idxC, idxB
		checkTree()

		# Move SubB to RootC and check the model again.
		mimeData = self.__makeMimeData(ctx.subB)
		self.assertTrue(self.__drop(mimeData, Qt.DropAction.MoveAction,
					    ctx.rootC))
		self.assertEqual(self.model.rowCount(), 2)
		idxA = self.model.index(0, 0)
		idxC = self.model.index(1, 0)
		self.assertEqual(self.model.modelIndexToTreeItem(idxA).entityId,
				 ctx.rootA.id)
		self.assertEqual(self.model.modelIndexToTreeItem(idxC).entityId,
				 ctx.rootC.id)
		self.assertEqual(self.model.rowCount(idxA), 1)
		self.assertEqual(self.model.rowCount(idxC), 1)
		idxB = self.model.index(0, 0, idxC)
		self.assertEqual(self.model.modelIndexToTreeItem(idxB).entityId,
				 ctx.subB.id)
		self.assertEqual(self.model.rowCount(idxB), 1)
		idxB1 = self.model.index(0, 0, idxB)
		self.assertEqual(self.model.modelIndexToTreeItem(idxB1).entityId,
				 ctx.itemB1.id)
		self.assertEqual(self.model.modelIndexToTreeItem(idxB1).entityType,
				 TreeItem.STOCKITEM)
