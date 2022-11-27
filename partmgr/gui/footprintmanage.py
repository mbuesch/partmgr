# -*- coding: utf-8 -*-
#
# PartMgr GUI - Footprint manage dialog
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

from partmgr.core.footprint import *
from partmgr.core.image import *


class FootprintEditWidget(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setLayout(QGridLayout(self))
		self.layout().setContentsMargins(QMargins())

		self.imageLabel = QLabel(self)
		self.imageLabel.setFrameShape(QFrame.Shape.Panel)
		self.imageLabel.setFrameShadow(QFrame.Shadow.Raised)
		self.imageLabel.setMinimumSize(QSize(50, 50))
		self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout().addWidget(self.imageLabel, 0, 0, 2, 1)

		self.imgImportButton = QPushButton("Import image", self)
		self.layout().addWidget(self.imgImportButton, 0, 1)

		self.imgClearButton = QPushButton("Clear image", self)
		self.layout().addWidget(self.imgClearButton, 1, 1)

		self.currentFootprint = None
		self.changeBlocked = 0

		self.imgImportButton.released.connect(self.__importImage)
		self.imgClearButton.released.connect(self.__clearImage)

	def updateData(self, footprint):
		self.changeBlocked += 1

		self.currentFootprint = footprint
		self.setEnabled(bool(footprint))

		self.imageLabel.clear()
		if footprint:
			pix = footprint.getImage().toPixmap()
			if pix.isNull():
				self.imageLabel.setText("< no image >")
			else:
				self.imageLabel.setPixmap(pix)

		self.changeBlocked -= 1

	def __importImage(self):
		if not self.currentFootprint:
			return
		fn, filt = QFileDialog.getOpenFileName(self,
			"Select image",
			"",
			"Image files (*.png *.jpg *.jpeg *.svg "
				     "*.gif *.bmp *.xpm *.xbm);;"
			"All files (*)")
		if not fn:
			return
		try:
			img = Image()
			img.fromFile(fn, None)
			img = img.scaleToMaxSize(QSize(150, 150))
			self.currentFootprint.setImage(img)
		except Error as e:
			QMessageBox.critical(self,
				"Image import failed",
				"Image import failed:\n" + str(e))
			return
		self.updateData(self.currentFootprint)

	def __clearImage(self):
		if not self.currentFootprint:
			return
		ret = QMessageBox.question(self,
			"Clear image?",
			"Clear image on footprint '%s'?" %\
			self.currentFootprint.getName(),
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if ret & QMessageBox.StandardButton.Yes == 0:
			return
		self.currentFootprint.setImage(Image())
		self.updateData(self.currentFootprint)

class FootprintManageDialog(AbstractEntityManageDialog):
	"Footprint create/modify/delete dialog"

	def __init__(self, db, parent=None):
		self.editWidget = FootprintEditWidget()
		AbstractEntityManageDialog.__init__(self, db,
			"Manage part footprints", self.editWidget,
			parent,
			AbstractEntityManageDialog.NO_PARAMETERS)

		self.nameLabel.setText("Footprint name:")

	def updateData(self, selectFootprint=None):
		AbstractEntityManageDialog.updateData(self,
			self.db.getFootprints(),
			selectFootprint)

	def entSelChanged(self, item=None, prevItem=None):
		AbstractEntityManageDialog.entSelChanged(self,
			item, prevItem)
		footprint = item.getEntity() if item else None
		self.editWidget.updateData(footprint)

	def newEntity(self):
		newFootprint = Footprint("Unnamed", db=self.db)
		self.db.modifyFootprint(newFootprint)
		self.updateData(newFootprint)
