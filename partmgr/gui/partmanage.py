# -*- coding: utf-8 -*-
#
# PartMgr GUI - Part manage dialog
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

from partmgr.gui.entitymanage import *
from partmgr.gui.util import *

from partmgr.core.part import *


class PartManageDialog(AbstractEntityManageDialog):
	"Part create/modify/delete dialog"

	def __init__(self, stockItem, parent=None):
		self.stockItem = stockItem
		AbstractEntityManageDialog.__init__(self, stockItem.db,
			"Manage parts", None, parent)

		self.nameLabel.setText("Part name:")

	def updateData(self, selectPart=None):
		AbstractEntityManageDialog.updateData(
			self, self.stockItem.getAllParts(),
			selectPart)

	def entSelChanged(self, item=None, prevItem=None):
		AbstractEntityManageDialog.entSelChanged(self,
			item, prevItem)

	def newEntity(self):
		newPart = Part("Unnamed",
			       category = self.stockItem.category,
			       db = self.stockItem.db)
		self.db.modifyPart(newPart)
		self.updateData(newPart)
