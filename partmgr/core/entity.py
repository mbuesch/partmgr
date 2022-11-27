# -*- coding: utf-8 -*-
#
# PartMgr - Abstract entity
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

from partmgr.core.timestamp import *
from partmgr.core.util import *


class Entity:
	"Abstract entity base class."

	FLG_OFFSET = 8	# Offset for user-flags

	NO_ID = -1	# Invalid ID

	# Set to PTYPE_..., if this entity supports parameters
	PARAMETER_PTYPE = None

	def __init__(self, name="", description="", flags=0,
		     createTimeStamp=None, modifyTimeStamp=None,
		     id=NO_ID, db=None, entityType="Entity"):
		self.name = name
		self.description = description
		self.flags = flags
		self.createTimeStamp = Timestamp(createTimeStamp)
		if not self.createTimeStamp.isValid():
			self.createTimeStamp.setNow()
		self.modifyTimeStamp = Timestamp(modifyTimeStamp)
		if not self.modifyTimeStamp.isValid():
			self.modifyTimeStamp.setStamp(self.createTimeStamp.getStamp())
		self.id = id
		self.db = db
		self.entityType = entityType

	def getId(self):
		return self.id

	def getName(self):
		return self.name

	def setName(self, newName):
		self.name = newName
		self.syncDatabase()

	def getDescription(self):
		return self.description

	def setDescription(self, newDescription):
		self.description = newDescription
		self.syncDatabase()

	def getCreateTimeStamp(self):
		return self.createTimeStamp.getStamp()

	def getModifyTimeStamp(self):
		return self.modifyTimeStamp.getStamp()

	def getAllParameters(self):
		assert(self.PARAMETER_PTYPE is not None)
		return self.db.getAllParametersByParent(self.PARAMETER_PTYPE, self)

	def addParameter(self, newParameter):
		assert(self.PARAMETER_PTYPE is not None)
		newParameter.setParentType(self.PARAMETER_PTYPE)
		newParameter.setParent(self)
		newParameter.id = Entity.NO_ID
		self.db.modifyParameter(newParameter)
		return newParameter

	@staticmethod
	def isValidId(entityId):
		if entityId is None:
			return False
		return entityId != Entity.NO_ID

	@staticmethod
	def toId(entity):
		if entity is None:
			return Entity.NO_ID
		if isinstance(entity, int):
			return entity
		assert(isinstance(entity, Entity))
		return entity.id

	def hasValidId(self):
		return Entity.isValidId(self.id)

	def getDatabase(self):
		return self.db

	def inDatabase(self, db):
		return self.db is db and self.hasValidId()

	def syncDatabase(self):
		pass # Override this in subclass, if required.

	def updateModifyTimeStamp(self):
		self.modifyTimeStamp.setNow()

	def delete(self):
		self.db = None
		self.id = Entity.NO_ID
		self.entityType = "Entity"

	def getEntityType(self):
		return self.entityType

	def __eq__(self, other):
		return isinstance(other, Entity) and\
		       self.entityType == other.entityType and\
		       self.db == other.db and\
		       self.id == other.id

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return (hash(self.entityType) ^
			hash(self.db) ^
			hash(self.id))

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.createTimeStamp))
		args.append(str(self.modifyTimeStamp))
		args.append(str(self.id))
		args.append(str(self.db))
		args.append(str(self.entityType))
		return "Entity(" + ", ".join(args) + ")"
