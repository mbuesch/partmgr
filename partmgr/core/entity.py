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
from partmgr.core.xmlfactory import XmlFactory
import contextlib

class Entity_XmlFactory(XmlFactory):
	def parser_open(self, tag=None, parentFactory=None):
		super().parser_open(self, tag)

	def parser_beginTag(self, tag):
		if tag.name == "entity":
			from partmgr.core.category import Category
			from partmgr.core.stockitem import StockItem

			entityType = tag.getAttr("entityType")
			type2class = {
				"category" : Category,
				"stockitem" : StockItem,
			}
			entityClass = None
			with contextlib.suppress(KeyError):
				entityClass = type2class[entityType]
			if entityClass:
				self.entity = entityClass(
					id=tag.getAttr("id"),
					name=tag.getAttr("name"),
					description=tag.getAttr("description"),
					flags=tag.getAttr("flags"),
					createTimeStamp=tag.getAttr("createTimeStamp"),
					modifyTimeStamp=tag.getAttr("modifyTimeStamp"),
				)
				self.parser_switchTo(entityClass.XmlFactory())
				return
		super().parser_beginTag(tag)

	def parser_endTag(self, tag):
		super().parser_endTag(tag)

	def composer_getTags(self):
		entity = self.entity
		return [ self.Tag(
			name="entity",
			attrs={
				"id" : str(entity.id),
				"name" : str(entity.name),
				"description" : str(entity.description),
				"flags" : str(entity.flags),
				"createTimeStamp" : str(entity.createTimeStamp.getStampInt()),
				"modifyTimeStamp" : str(entity.modifyTimeStamp.getStampInt()),
				"entityType" : str(entity.entityType).lower(),
			},
		) ]

class Entity:
	"Abstract entity base class."

	XmlFactory = Entity_XmlFactory

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
