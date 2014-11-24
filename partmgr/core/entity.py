# -*- coding: utf-8 -*-
#
# PartMgr - Abstract entity
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

from partmgr.core.util import *


class Entity(object):
	"Abstract entity base class."

	NO_ID = -1	# Invalid ID

	def __init__(self, name="", description="",
		     id=NO_ID, db=None, entityType="Entity"):
		self.name = name
		self.description = description
		self.id = id
		self.db = db
		self.entityType = entityType

	def getId(self):
		return self.id

	def getName(self):
		return self.name

	def getVerboseName(self):
		return self.getName()

	def setName(self, newName):
		self.name = newName
		self.syncDatabase()

	def getDescription(self):
		return self.description

	def setDescription(self, newDescription):
		self.description = newDescription
		self.syncDatabase()

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
		return entity.id

	def hasValidId(self):
		return Entity.isValidId(self.id)

	def getDatabase(self):
		return self.db

	def inDatabase(self, db):
		return self.db is db and self.hasValidId()

	def syncDatabase(self):
		pass # Override this in subclass, if required.

	def delete(self):
		self.db = None
		self.id = Entity.NO_ID
		self.entityType = "Entity"

	def getEntityType(self):
		return self.entityType

	def __eq__(self, other):
		return other and\
		       self.db == other.db and\
		       self.id == other.id

	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		args = []
		args.append(str(self.id))
		args.append(str(self.db))
		return "Entity(" + ", ".join(args) + ")"
