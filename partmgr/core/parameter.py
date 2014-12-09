# -*- coding: utf-8 -*-
#
# PartMgr - Parameter descriptor
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


class Parameter(Entity):
	"Parameter descriptor."

	# Parent types
	PTYPE_GLOBAL	= 0
	PTYPE_PART	= 1
	PTYPE_CATEGORY	= 2
	PTYPE_SUPPLIER	= 3
	PTYPE_LOCATION	= 4
	PTYPE_FOOTPRINT	= 5
	PTYPE_STOCKITEM	= 6
	PTYPE_ORIGIN	= 7
	PTYPE_STORAGE	= 8

	def __init__(self, name,
		     parentType=PTYPE_GLOBAL,
		     parent=None,
		     data=b"",
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Parameter",
				**kwds)
		self.parentType = parentType
		self.parent = Entity.toId(parent)
		self.__setData(data)

	def syncDatabase(self):
		if self.db:
			self.db.modifyParameter(self)

	def setParentType(self, parentType):
		self.parentType = self.toId(parentType)
		self.syncDatabase()

	def getParentType(self):
		return self.parentType

	def setParent(self, parent):
		self.parent = Entity.toId(parent)
		self.syncDatabase()

	def getData(self):
		return self.data

	def getDataString(self):
		try:
			return self.getData().decode(STR_ENCODING)
		except UnicodeDecodeError as e:
			raise PartMgrError("%s: data string decode error: %s" %\
				    (str(self), str(e)))

	def getDataInt(self):
		try:
			return int(self.getDataString())
		except ValueError as e:
			raise PartMgrError("%s: data int decode error: %s" %\
				    (str(self), str(e)))

	def __setData(self, newData):
		try:
			if isinstance(newData, str):
				self.data = newData.encode(STR_ENCODING)
			elif isinstance(newData, bytes):
				self.data = newData
			elif isinstance(newData, int):
				self.data = str(newData).encode(STR_ENCODING)
			else:
				assert(0)
		except UnicodeEncodeError as e:
			raise PartMgrError("%s: data string encode error: %s" %\
				    (str(self), str(e)))

	def setData(self, newData):
		self.__setData(newData)
		self.syncDatabase()

	def delete(self):
		self.db.delParameter(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.parentType))
		args.append(str(self.parent))
		args.append(str(self.data))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Parameter(" + ", ".join(args) + ")"

class Param_Currency(Parameter):
	# "currency" parameter data
	CURR_EUR	= 0
	CURR_USD	= 1

	# currency name string table
	CURRNAMES = {
		CURR_EUR	: ("EUR", "Euro"),
		CURR_USD	: ("USD", "US Dollar"),
	}
