# -*- coding: utf-8 -*-
#
# PartMgr - Stock item descriptor
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

from partmgr.core.entity import *
from partmgr.core.util import *


class StockItem(Entity):
	"Stock item descriptor."

	# Units (this is database format ABI)
	UNIT_PC		= 0	# Pieces
	UNIT_PACK	= 1	# Packages

	UNIT_MM		= 100	# Millimeter
	UNIT_CM		= 101	# Centimeter
	UNIT_DM		= 102	# Decimeter
	UNIT_M		= 103	# Meter
	UNIT_KM		= 104	# Kilometer
	UNIT_AU		= 190	# Astronomical units

	UNIT_MG		= 200	# Milligrams
	UNIT_G		= 201	# Grams
	UNIT_KG		= 202	# Kilograms
	UNIT_T		= 203	# Tons

	UNIT_SMM	= 300	# Square millimeter
	UNIT_SCM	= 301	# Square centimeter
	UNIT_SDM	= 302	# Square decimeter
	UNIT_SM		= 303	# Square meter

	UNIT_ML		= 400	# Milliliter
	UNIT_CL		= 401	# Centiliter
	UNIT_L		= 402	# Liter

	UNIT_CMM	= 500	# Cubic millimeter
	UNIT_CCM	= 501	# Cubic centimeter
	UNIT_CDM	= 502	# Cubic decimeter
	UNIT_CUM	= 503	# Cubic meter

	UNITNAMES = {
		UNIT_PC		: ("pc", "pieces"),
		UNIT_PACK	: ("pack", "packages"),
		UNIT_MM		: ("mm", "millimeter"),
		UNIT_CM		: ("cm", "centimeter"),
		UNIT_DM		: ("dm", "decimeter"),
		UNIT_M		: ("m", "meter"),
		UNIT_KM		: ("km", "kilometer"),
		UNIT_AU		: ("au", "astronomical units"),
		UNIT_MG		: ("mg", "milligrams"),
		UNIT_G		: ("g", "grams"),
		UNIT_KG		: ("kg", "kilograms"),
		UNIT_T		: ("t", "tons"),
		UNIT_SMM	: ("mm^2", "square millimeter"),
		UNIT_SCM	: ("cm^2", "square centimeter"),
		UNIT_SDM	: ("dm^2", "square decimeter"),
		UNIT_SM		: ("m^2", "square meter"),
		UNIT_ML		: ("ml", "milliliter"),
		UNIT_CL		: ("cl", "centiliter"),
		UNIT_L		: ("l", "liter"),
		UNIT_CMM	: ("mm^3", "cubic millimeter"),
		UNIT_CCM	: ("cm^3", "cubic centimeter"),
		UNIT_CDM	: ("dm^3", "cubic decimeter"),
		UNIT_CUM	: ("m^3", "cubic meter"),
	}

	def __init__(self, name, description,
		     part, category, footprint,
		     minQuantity, targetQuantity, quantityUnits,
		     id=Entity.NO_ID, db=None):
		Entity.__init__(self, name, description,
				id, db, "StockItem")
		self.part = Entity.toId(part)
		self.category = Entity.toId(category)
		self.footprint = Entity.toId(footprint)
		self.minQuantity = minQuantity
		self.targetQuantity = targetQuantity
		self.quantityUnits = quantityUnits

	def syncDatabase(self):
		if self.db:
			self.db.modifyStockItem(self)

	def getVerboseName(self):
		name = self.getName()
		if name:
			return name
		part = self.getPart()
		if part:
			return part.getName()
		return "Unnamed item"

	def setName(self, newName):
		part = self.getPart()
		if part:
			if newName == part.getName():
				newName = ""
		Entity.setName(self, newName)

	def getPart(self):
		if not Entity.isValidId(self.part):
			return None
		return self.db.getPart(self.part)

	def setPart(self, newPart):
		self.part = self.toId(newPart)
		self.syncDatabase()

	def setCategory(self, category):
		self.category = self.toId(category)
		self.syncDatabase()

	def hasCategory(self):
		return Entity.isValidId(self.category)

	def getCategory(self):
		assert(self.hasCategory())
		return self.db.getCategory(self.category)

	def getParent(self):
		return self.getCategory()

	def getFootprint(self):
		if not Entity.isValidId(self.footprint):
			return None
		return self.db.getFootprint(self.footprint)

	def setFootprint(self, newFootprint):
		self.footprint = self.toId(newFootprint)
		self.syncDatabase()

	def getGlobalQuantity(self):
		return sum(s.getQuantity() for s in self.getStorages())

	def getOrderQuantity(self):
		"Get global number of parts to order. Might be negative!"
		targetQty = max(self.getMinQuantity(),
				self.getTargetQuantity())
		return targetQty - self.getGlobalQuantity()

	def getMinQuantity(self):
		return self.minQuantity

	def setMinQuantity(self, newMinQuantity):
		self.minQuantity = newMinQuantity
		self.syncDatabase()

	def getTargetQuantity(self):
		return self.targetQuantity

	def setTargetQuantity(self, newTargetQuantity):
		self.targetQuantity = newTargetQuantity
		self.syncDatabase()

	@staticmethod
	def getAllQuantityUnits():
		unitsList = list(StockItem.UNITNAMES.keys())
		unitsList.sort(key = lambda u: u)
		return unitsList

	@staticmethod
	def quantityShortName(units):
		return StockItem.UNITNAMES[units][0]

	@staticmethod
	def quantityLongName(units):
		return StockItem.UNITNAMES[units][1]

	def getQuantityUnitsShort(self):
		return self.quantityShortName(self.getQuantityUnits())

	def getQuantityUnitsLong(self):
		return self.quantityLongName(self.getQuantityUnits())

	def getQuantityUnits(self):
		return self.quantityUnits

	def setQuantityUnits(self, newUnits):
		self.quantityUnits = newUnits
		self.syncDatabase()

	def getOrigins(self):
		return self.db.getOriginsByStockItem(self)

	def getStorages(self):
		return self.db.getStoragesByStockItem(self)

	def delete(self):
		self.db.delStockItem(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.category))
		args.append(str(self.footprint))
		args.append(str(self.minQuantity))
		args.append(str(self.targetQuantity))
		args.append(str(self.quantityUnits))
		args.append(str(self.id))
		args.append(str(self.db))
		return "StockItem(" + ", ".join(args) + ")"
