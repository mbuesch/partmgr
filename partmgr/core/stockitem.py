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

	UNIT_PM		= 100	# Picometer
	UNIT_NM		= 101	# Nanometer
	UNIT_UM		= 102	# Micrometer
	UNIT_MM		= 103	# Millimeter
	UNIT_CM		= 104	# Centimeter
	UNIT_DM		= 105	# Decimeter
	UNIT_M		= 106	# Meter
	UNIT_KM		= 107	# Kilometer
	UNIT_AU		= 150	# Astronomical units

	UNIT_PG		= 200	# Picograms
	UNIT_NG		= 201	# Nanograms
	UNIT_UG		= 202	# Micrograms
	UNIT_MG		= 203	# Milligrams
	UNIT_G		= 204	# Grams
	UNIT_KG		= 205	# Kilograms
	UNIT_T		= 206	# Tons

	UNIT_SPM	= 300	# Square picometer
	UNIT_SNM	= 301	# Square nanometer
	UNIT_SUM	= 302	# Square micrometer
	UNIT_SMM	= 303	# Square millimeter
	UNIT_SCM	= 304	# Square centimeter
	UNIT_SDM	= 305	# Square decimeter
	UNIT_SM		= 306	# Square meter

	UNIT_PL		= 400	# Picoliter
	UNIT_NL		= 401	# Nanoliter
	UNIT_UL		= 402	# Microliter
	UNIT_ML		= 403	# Milliliter
	UNIT_CL		= 404	# Centiliter
	UNIT_L		= 405	# Liter

	UNIT_CPM	= 500	# Cubic picometer
	UNIT_CNM	= 501	# Cubic nanometer
	UNIT_CUM	= 502	# Cubic micrometer
	UNIT_CMM	= 503	# Cubic millimeter
	UNIT_CCM	= 504	# Cubic centimeter
	UNIT_CDM	= 505	# Cubic decimeter
	UNIT_CUBM	= 506	# Cubic meter

	UNITNAMES = {
		UNIT_PC		: ("pc", "pieces"),
		UNIT_PACK	: ("pack", "packages"),
		UNIT_PM		: ("pm", "picometer"),
		UNIT_NM		: ("nm", "nanometer"),
		UNIT_UM		: ("µm", "micrometer"),
		UNIT_MM		: ("mm", "millimeter"),
		UNIT_CM		: ("cm", "centimeter"),
		UNIT_DM		: ("dm", "decimeter"),
		UNIT_M		: ("m", "meter"),
		UNIT_KM		: ("km", "kilometer"),
		UNIT_AU		: ("au", "astronomical units"),
		UNIT_PG		: ("pg", "picograms"),
		UNIT_NG		: ("ng", "nanograms"),
		UNIT_UG		: ("µg", "micrograms"),
		UNIT_MG		: ("mg", "milligrams"),
		UNIT_G		: ("g", "grams"),
		UNIT_KG		: ("kg", "kilograms"),
		UNIT_T		: ("t", "metric tons"),
		UNIT_SPM	: ("pm^2", "square picometer"),
		UNIT_SNM	: ("nm^2", "square nanometer"),
		UNIT_SUM	: ("µm^2", "square micrometer"),
		UNIT_SMM	: ("mm^2", "square millimeter"),
		UNIT_SCM	: ("cm^2", "square centimeter"),
		UNIT_SDM	: ("dm^2", "square decimeter"),
		UNIT_SM		: ("m^2", "square meter"),
		UNIT_PL		: ("pl", "picoliter"),
		UNIT_NL		: ("nl", "nanoliter"),
		UNIT_UL		: ("µl", "microliter"),
		UNIT_ML		: ("ml", "milliliter"),
		UNIT_CL		: ("cl", "centiliter"),
		UNIT_L		: ("l", "liter"),
		UNIT_CPM	: ("pm^3", "cubic picometer"),
		UNIT_CNM	: ("nm^3", "cubic nanometer"),
		UNIT_CUM	: ("µm^3", "cubic micrometer"),
		UNIT_CMM	: ("mm^3", "cubic millimeter"),
		UNIT_CCM	: ("cm^3", "cubic centimeter"),
		UNIT_CDM	: ("dm^3", "cubic decimeter"),
		UNIT_CUBM	: ("m^3", "cubic meter"),
	}

	def __init__(self, name,
		     part=None, category=None, footprint=None,
		     minQuantity=0, targetQuantity=0, quantityUnits=UNIT_PC,
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "StockItem",
				**kwds)
		self.part = Entity.toId(part)
		self.category = Entity.toId(category)
		self.footprint = Entity.toId(footprint)
		self.minQuantity = minQuantity
		self.targetQuantity = targetQuantity
		self.quantityUnits = quantityUnits

	def syncDatabase(self):
		if self.db:
			self.db.modifyStockItem(self)

	def getName(self):
		name = Entity.getName(self)
		if not name:
			part = self.getPart()
			partName = part.getName() if part else None
			if partName:
				# This is a compat and convenience hack.
				# If this stock item doesn't have a name, but
				# has a named part, we take its name.
				name = partName
				self.setName(name)
		return name

	def getPart(self):
		if not Entity.isValidId(self.part):
			return None
		return self.db.getPart(self.part)

	def setPart(self, newPart):
		self.part = self.toId(newPart)
		self.syncDatabase()

	def getAllParts(self):
		return self.db.getPartsByCategory(self.category)

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
		args.append(str(self.flags))
		args.append(str(self.category))
		args.append(str(self.footprint))
		args.append(str(self.minQuantity))
		args.append(str(self.targetQuantity))
		args.append(str(self.quantityUnits))
		args.append(str(self.id))
		args.append(str(self.db))
		return "StockItem(" + ", ".join(args) + ")"
