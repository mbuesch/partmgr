# -*- coding: utf-8 -*-
#
# PartMgr - Footprint descriptor
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
from partmgr.core.image import *
from partmgr.core.util import *


class Footprint(Entity):
	"Footprint descriptor."

	def __init__(self, name,
		     image=None,
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Footprint",
				**kwds)
		if not image:
			image = Image()
		self.image = image

	def syncDatabase(self):
		if self.db:
			self.db.modifyFootprint(self)

	def getImage(self):
		return self.image

	def setImage(self, newImage):
		self.image = newImage
		self.syncDatabase()

	def delete(self):
		self.db.delFootprint(self)
		Entity.delete(self)

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.image))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Footprint(" + ", ".join(args) + ")"
