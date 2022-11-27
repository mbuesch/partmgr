# -*- coding: utf-8 -*-
#
# PartMgr - Image
#
# Copyright 2014-2022 Michael Buesch <m@bues.ch>
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


class Image:
	def __init__(self, data=None):
		self.convertFrom(data)

	def isNull(self):
		return self.pixmap.isNull()

	def convertFrom(self, data, dataFormat="PNG"):
		self.pixmap = QPixmap()
		if not data:
			return
		if isinstance(data, str):
			data = fromBase64(data, toBytes=True)
			if not data:
				return
		if isinstance(data, bytes):
			data = QByteArray(data)
		if isinstance(data, QByteArray):
			pix = QPixmap()
			pix.loadFromData(data, dataFormat)
			data = pix
		if not isinstance(data, QPixmap):
			raise PartMgrError("Unsupported Image object type")
		self.pixmap = data

	def fromFile(self, filename, fileFormat):
		try:
			fd = open(filename, "rb")
			data = fd.read()
			fd.close()
		except IOError as e:
			raise PartMgrError("Failed to read %s: %s" %\
				    (filename, str(e)))
		self.convertFrom(data, fileFormat)
		if self.isNull():
			raise PartMgrError("%s: Unknown image format" % filename)

	def toString(self):
		return toBase64(self.toBytes())

	def toBytes(self):
		return self.toQByteArray().data()

	def toQByteArray(self):
		ba = QByteArray()
		buf = QBuffer(ba)
		buf.open(QIODeviceBase.OpenModeFlag.WriteOnly)
		self.toPixmap().save(buf, "PNG")
		return ba

	def toPixmap(self):
		return self.pixmap

	def size(self):
		return self.pixmap.size()

	def scaleToMaxSize(self, maxSize):
		if self.size().height() <= maxSize.height() and\
		   self.size().width() <= maxSize.width():
			return self
		return Image(self.pixmap.scaled(
				maxSize,
				Qt.AspectRatioMode.KeepAspectRatio,
				Qt.TransformationMode.SmoothTransformation))
