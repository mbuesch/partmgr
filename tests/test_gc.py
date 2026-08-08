#
# PartMgr - Unit tests for database garbage collection
#
# Copyright 2026 Michael Buesch <m@bues.ch>
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
from partmgr.core.entity import Entity
from partmgr.core.category import Category
from partmgr.core.stockitem import StockItem
from partmgr.core.part import Part
from partmgr.core.origin import Origin
from partmgr.core.storage import Storage
from partmgr.core.supplier import Supplier
from partmgr.core.location import Location
from partmgr.core.footprint import Footprint
from partmgr.core.parameter import Parameter


class Test_GarbageCollect(TestCase):

	@classmethod
	def setUpClass(cls):
		# Footprint images require a QGuiApplication.
		from partmgr.qt_bindings import QApplication
		cls.app = QApplication.instance() or QApplication([])

	def test_unreachableItemsDeletedOnClose(self):
		tmp = tempfile.TemporaryDirectory(prefix="partmgr-test-")
		dbFile = os.path.join(tmp.name, "test.pmg")
		try:
			db = Database(dbFile)

			# Primary items. These must survive garbage
			# collection, even if nothing references them.
			root = Category("Root")
			db.modifyCategory(root)
			child = Category("Child", parent=root)
			db.modifyCategory(child)
			supplier = Supplier("Supplier")
			db.modifySupplier(supplier)
			location = Location("Location")
			db.modifyLocation(location)
			footprint = Footprint("Footprint")
			db.modifyFootprint(footprint)

			# A stock item with secondary items attached.
			partUsed = Part("PartUsed", category=root)
			db.modifyPart(partUsed)
			item = StockItem("Item",
					 part=partUsed,
					 category=root,
					 footprint=footprint)
			db.modifyStockItem(item)
			origin = Origin("Origin",
					stockItem=item,
					supplier=supplier,
					orderCode="123",
					price=1.0)
			db.modifyOrigin(origin)
			storage = Storage("Storage",
					  stockItem=item,
					  location=location,
					  quantity=10)
			db.modifyStorage(storage)

			# A part that is not referenced by any stock item.
			partOrphan = Part("PartOrphan", category=root)
			db.modifyPart(partOrphan)

			# Parameters on various parents.
			db.modifyParameter(Parameter("p-global",
				parentType=Parameter.PTYPE_GLOBAL))
			db.modifyParameter(Parameter("p-category",
				parentType=Parameter.PTYPE_CATEGORY,
				parent=root))
			db.modifyParameter(Parameter("p-supplier",
				parentType=Parameter.PTYPE_SUPPLIER,
				parent=supplier))
			db.modifyParameter(Parameter("p-location",
				parentType=Parameter.PTYPE_LOCATION,
				parent=location))
			db.modifyParameter(Parameter("p-footprint",
				parentType=Parameter.PTYPE_FOOTPRINT,
				parent=footprint))
			db.modifyParameter(Parameter("p-part-used",
				parentType=Parameter.PTYPE_PART,
				parent=partUsed))
			db.modifyParameter(Parameter("p-part-orphan",
				parentType=Parameter.PTYPE_PART,
				parent=partOrphan))
			db.modifyParameter(Parameter("p-stockitem",
				parentType=Parameter.PTYPE_STOCKITEM,
				parent=item))
			db.modifyParameter(Parameter("p-origin",
				parentType=Parameter.PTYPE_ORIGIN,
				parent=origin))
			db.modifyParameter(Parameter("p-storage",
				parentType=Parameter.PTYPE_STORAGE,
				parent=storage))

			# Delete the stock item. This orphans the part,
			# the origin, the storage and all parameters
			# attached to any of these.
			db.delStockItem(item)

			# Closing the database collects the garbage.
			db.close()

			# Reopen the database and check what survived.
			db = Database(dbFile)

			# Primary items survive.
			self.assertIsNotNone(db.getCategory(root.id))
			self.assertIsNotNone(db.getCategory(child.id))
			self.assertIsNotNone(db.getSupplier(supplier.id))
			self.assertIsNotNone(db.getLocation(location.id))
			self.assertIsNotNone(db.getFootprint(footprint.id))

			# Unreachable secondary items are gone.
			self.assertIsNone(db.getPart(partUsed.id))
			self.assertIsNone(db.getPart(partOrphan.id))
			self.assertIsNone(db.getOrigin(origin.id))
			self.assertIsNone(db.getStorage(storage.id))
			self.assertEqual(db.getParts(), [])

			# Parameters of surviving parents survive.
			self.assertIsNotNone(db.getGlobalParameter("p-global"))
			for parentType, parent in (
				(Parameter.PTYPE_CATEGORY, root.id),
				(Parameter.PTYPE_SUPPLIER, supplier.id),
				(Parameter.PTYPE_LOCATION, location.id),
				(Parameter.PTYPE_FOOTPRINT, footprint.id),
			):
				params = db.getAllParametersByParent(parentType,
								     parent)
				self.assertEqual(len(params), 1)

			# Parameters of deleted parents are gone.
			for parentType, parent in (
				(Parameter.PTYPE_PART, partUsed.id),
				(Parameter.PTYPE_PART, partOrphan.id),
				(Parameter.PTYPE_STOCKITEM, item.id),
				(Parameter.PTYPE_ORIGIN, origin.id),
				(Parameter.PTYPE_STORAGE, storage.id),
			):
				params = db.getAllParametersByParent(parentType,
								     parent)
				self.assertEqual(len(params), 0)

			db.close()
		finally:
			tmp.cleanup()

	def test_referencedItemsSurvive(self):
		tmp = tempfile.TemporaryDirectory(prefix="partmgr-test-")
		dbFile = os.path.join(tmp.name, "test.pmg")
		try:
			db = Database(dbFile)

			root = Category("Root")
			db.modifyCategory(root)

			# A part shared by two stock items.
			sharedPart = Part("SharedPart", category=root)
			db.modifyPart(sharedPart)
			itemA = StockItem("ItemA",
					  part=sharedPart,
					  category=root)
			db.modifyStockItem(itemA)
			itemB = StockItem("ItemB",
					  part=sharedPart,
					  category=root)
			db.modifyStockItem(itemB)
			originB = Origin("OriginB", stockItem=itemB)
			db.modifyOrigin(originB)
			storageB = Storage("StorageB",
					   stockItem=itemB,
					   quantity=1)
			db.modifyStorage(storageB)
			db.modifyParameter(Parameter("p-sharedpart",
				parentType=Parameter.PTYPE_PART,
				parent=sharedPart))

			# Delete only one of the stock items.
			db.delStockItem(itemA)

			# Closing the database collects the garbage.
			db.close()

			# Reopen the database and check what survived.
			db = Database(dbFile)

			# The shared part is still referenced by itemB
			# and therefore must survive, along with the
			# secondary items of itemB.
			self.assertIsNotNone(db.getPart(sharedPart.id))
			self.assertIsNotNone(db.getStockItem(itemB.id))
			self.assertIsNotNone(db.getOrigin(originB.id))
			self.assertIsNotNone(db.getStorage(storageB.id))
			params = db.getAllParametersByParent(
				Parameter.PTYPE_PART, sharedPart.id)
			self.assertEqual(len(params), 1)

			db.close()
		finally:
			tmp.cleanup()
