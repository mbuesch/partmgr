# -*- coding: utf-8 -*-
#
# PartMgr GUI - Part select widget
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

from partmgr.gui.itemselect import *
from partmgr.gui.partmanage import *
from partmgr.gui.util import *


class PartSelectWidget(ItemSelectWidget):
	def __init__(self, parent=None):
		ItemSelectWidget.__init__(self, parent,
			actionButtonLabel = "Manage parts")
		self.stockItem = None

	def updateData(self, stockItem, selectedPart=None):
		self.stockItem = stockItem
		ItemSelectWidget.updateData(self, stockItem.getAllParts(), selectedPart)

	def actionButtonPressed(self):
		dlg = PartManageDialog(self.stockItem, self)
		part = self.getSelected()
		dlg.edit(part)
		self.updateData(self.stockItem, part)
