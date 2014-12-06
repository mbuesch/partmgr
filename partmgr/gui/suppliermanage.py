# -*- coding: utf-8 -*-
#
# PartMgr GUI - Supplier manage dialog
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

from partmgr.core.supplier import *


class SupplierEditWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(QMargins())

		label = QLabel("URL:", self)
		self.layout().addWidget(label, 0, 0)

		self.urlEdit = QLineEdit(self)
		self.layout().addWidget(self.urlEdit, 0, 1)

		self.currentSupplier = None
		self.changeBlocked = 0

		self.urlEdit.textChanged.connect(self.__urlChanged)

	def updateData(self, supplier):
		self.changeBlocked += 1

		self.currentSupplier = supplier

		self.urlEdit.setEnabled(bool(supplier))
		self.urlEdit.clear()
		if supplier:
			self.urlEdit.setText(supplier.getUrl())

		self.changeBlocked -= 1

	def __urlChanged(self, newUrl):
		if self.changeBlocked:
			return
		if not self.currentSupplier:
			return
		self.currentSupplier.setUrl(newUrl)

class SupplierManageDialog(AbstractEntityManageDialog):
	"Suppliers create/modify/delete dialog"

	def __init__(self, db, parent=None):
		self.editWidget = SupplierEditWidget()
		AbstractEntityManageDialog.__init__(self, db,
			"Manage suppliers", self.editWidget,
			parent,
			AbstractEntityManageDialog.NO_PARAMETERS)

		self.nameLabel.setText("Supplier name:")

	def updateData(self, selectSupplier=None):
		AbstractEntityManageDialog.updateData(self,
			self.db.getSuppliers(),
			selectSupplier)

	def entSelChanged(self, item=None, prevItem=None):
		AbstractEntityManageDialog.entSelChanged(self,
			item, prevItem)
		supplier = item.getEntity() if item else None
		self.editWidget.updateData(supplier)

	def newEntity(self):
		newSupplier = Supplier("Unnamed", db=self.db)
		self.db.modifySupplier(newSupplier)
		self.updateData(newSupplier)
