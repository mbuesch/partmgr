# -*- coding: utf-8 -*-
#
# PartMgr GUI - Quantity widgets
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

from partmgr.gui.protected_spinbox import *
from partmgr.gui.util import *


class QuantitySpinBox(ProtectedSpinBox):
	def __init__(self, parent=None):
		ProtectedSpinBox.__init__(self, parent)
		self.setMinimum(0)
		self.setMaximum(0x7FFFFFFF)
		self.setValue(0)
		self.setSingleStep(1)

class QuantityWidget(QWidget):
	quantityChanged = Signal(int)

	def __init__(self, storage, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QVBoxLayout(self))
		self.layout().setContentsMargins(QMargins())

		label = QLabel("Quantity:", self)
		self.layout().addWidget(label)

		self.quantity = QuantitySpinBox(self)
		self.quantity.setValue(storage.getQuantity())
		self.quantity.setProtected(False)
		suffix = storage.getStockItem().getQuantityUnitsShort()
		self.quantity.setSuffix(" " + suffix)
		self.layout().addWidget(self.quantity)

		self.quantity.valueChanged.connect(self.quantityChanged)
