# -*- coding: utf-8 -*-
#
# PartMgr GUI - Footprint select widget
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
from partmgr.gui.util import *


class FootprintSelectWidget(ItemSelectWidget):
	def __init__(self, parent=None):
		ItemSelectWidget.__init__(self, parent)
		self.db = None

	def update(self, db, selected=None):
		self.db = db
		ItemSelectWidget.update(self, db.getFootprints(), selected)
