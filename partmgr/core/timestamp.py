# -*- coding: utf-8 -*-
#
# PartMgr - Timestamp
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

import datetime


class Timestamp:
	def __init__(self, stamp=None):
		self.setStamp(stamp)

	def isValid(self):
		return self.getStampInt() > 0

	def setStamp(self, stamp):
		if not stamp:
			stamp = 0
		if isinstance(stamp, datetime.datetime):
			stamp = int(round(stamp.timestamp()))
		self.stamp = int(stamp)

	def setNow(self):
		self.setStamp(datetime.datetime.utcnow())

	def getStamp(self):
		if not self.isValid():
			return None
		return datetime.datetime.fromtimestamp(self.getStampInt())

	def getStampInt(self):
		return self.stamp

	def __repr__(self):
		return str(self.getStamp())
