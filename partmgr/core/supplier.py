# -*- coding: utf-8 -*-
#
# PartMgr - Supplier descriptor
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


class Supplier(Entity):
	"Supplier descriptor."

	def __init__(self, name,
		     url="",
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Supplier",
				**kwds)
		self.url = url

	def syncDatabase(self):
		if self.db:
			self.db.modifySupplier(self)

	def getUrl(self):
		return self.url

	def setUrl(self, newUrl):
		self.url = newUrl
		self.syncDatabase()

	def delete(self):
		self.db.delSupplier(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.url))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Supplier(" + ", ".join(args) + ")"
