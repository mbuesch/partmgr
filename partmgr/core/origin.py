# -*- coding: utf-8 -*-
#
# PartMgr - Origin descriptor
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
from partmgr.core.timestamp import *
from partmgr.core.util import *


class Origin(Entity):
	"Item origin descriptor."

	NO_PRICE = -0.1

	def __init__(self, name,
		     stockItem=None, supplier=None, orderCode="",
		     price=NO_PRICE, priceTimeStamp=None,
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Origin",
				**kwds)
		self.stockItem = Entity.toId(stockItem)
		self.supplier = Entity.toId(supplier)
		self.orderCode = orderCode
		self.price = float(price)
		self.priceStamp = Timestamp(priceTimeStamp)

	def syncDatabase(self):
		if self.db:
			self.db.modifyOrigin(self)

	def getStockItem(self):
		return self.db.getStockItem(self.stockItem)

	def getSupplier(self):
		if not Entity.isValidId(self.supplier):
			return None
		return self.db.getSupplier(self.supplier)

	def setSupplier(self, newSupplier):
		self.supplier = Entity.toId(newSupplier)
		self.syncDatabase()

	def getOrderCode(self):
		return self.orderCode

	def setOrderCode(self, newOrderCode):
		self.orderCode = newOrderCode
		self.syncDatabase()

	def hasPrice(self):
		return self.price >= 0.0

	def getPrice(self):
		if not self.hasPrice():
			return None
		return self.price

	def setPrice(self, newPrice, updateTimeStamp=True):
		if newPrice is None:
			newPrice = self.NO_PRICE
		self.price = round(float(newPrice), 5)
		if updateTimeStamp:
			self.setPriceTimeStampNow()
		self.syncDatabase()

	def setPriceTimeStampNow(self):
		self.priceStamp.setNow()
		self.syncDatabase()

	def setPriceTimeStamp(self, newStamp):
		self.priceStamp.setStamp(newStamp)
		self.syncDatabase()

	def getPriceTimeStamp(self):
		return self.priceStamp.getStamp()

	def getPriceTimeStampInt(self):
		return self.priceStamp.getStampInt()

	def delete(self):
		self.db.delOrigin(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.stockItem))
		args.append(str(self.supplier))
		args.append(str(self.orderCode))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Origin(" + ", ".join(args) + ")"
