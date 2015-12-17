# -*- coding: utf-8 -*-
#
# PartMgr - Part descriptor
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
from partmgr.core.parameter import *


class Part(Entity):
	"Part descriptor."

	PARAMETER_PTYPE = Parameter.PTYPE_PART

	def __init__(self, name,
		     category=None,
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Part",
				**kwds)
		self.category = Entity.toId(category)

	def syncDatabase(self):
		if self.db:
			self.db.modifyPart(self)

	def setCategory(self, category):
		self.category = self.toId(category)
		self.syncDatabase()

	def hasCategory(self):
		return Entity.isValidId(self.category)

	def getCategory(self):
		assert(self.hasCategory())
		return self.db.getCategory(self.category)

	def delete(self):
		self.db.delPart(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.category))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Part(" + ", ".join(args) + ")"
