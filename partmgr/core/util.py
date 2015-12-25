# -*- coding: utf-8 -*-
#
# PartMgr - Utils
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

import base64

from partmgr.qt_bindings import *

from partmgr.core.exception import *
from partmgr.core.version import *


STR_ENCODING = "UTF-8"

def toBase64(value):
	try:
		if isinstance(value, str):
			value = value.encode(STR_ENCODING) # To bytes
		value = base64.standard_b64encode(value)
		return value.decode(STR_ENCODING) # To str
	except UnicodeError as e:
		raise PartMgrError("toBase64: %s" % str(e))

def fromBase64(value, toBytes=False):
	try:
		if isinstance(value, str):
			value = value.encode(STR_ENCODING) # To bytes
		value = base64.standard_b64decode(value)
		if toBytes:
			return value
		return value.decode(STR_ENCODING) # To str
	except UnicodeError as e:
		raise PartMgrError("fromBase64: %s" % str(e))
