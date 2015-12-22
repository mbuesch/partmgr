# -*- coding: utf-8 -*-
#
# PartMgr - Price fetching
#
# Copyright 2015 Michael Buesch <m@bues.ch>
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

from partmgr.core.parameter import *
from partmgr.core.util import *

import http.client
import urllib.parse


class PriceFetcher(object):
	"""Part price fetcher."""

	class Error(Exception):
		pass

	class Result(object):
		FOUND = True
		NOTFOUND = False

		def __init__(self,
			     orderCode = None,
			     price = 0.0,
			     status = FOUND,
			     currency = Param_Currency.CURR_EUR):
			self.orderCode = orderCode
			self.price = price
			self.status = status
			self.currency = currency

		def __repr__(self):
			if self.status == self.FOUND:
				curr = Param_Currency.CURRNAMES[self.currency][0]
				return "%s: %.2f %s" % (
					self.orderCode, self.price, curr)
			else:
				return "%s: not found" % self.orderCode

	supplierName = None
	host = None

	_registeredFetchers = []

	_defaultHttpHeader = {
		"User-Agent" : "PartMgrBot/1.0 (+https://www.example.com/)",
		"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language" : "*",
		"Accept-Charset" : "utf-8,*;q=0.9",
	}

	@classmethod
	def register(cls):
		PriceFetcher._registeredFetchers.append(cls)

	@classmethod
	def get(cls, wantedSupplierName):
		wantedSupplierName = wantedSupplierName.lower().strip()
		for fetcher in cls._registeredFetchers:
			supplierName = fetcher.supplierName.lower().strip()
			if supplierName == wantedSupplierName:
				return fetcher
		return None

	def __init__(self, tls = True):
		self.conn = None
		self.tls = tls

	def __del__(self):
		try:
			self.disconnect()
		except Exception as e:
			pass

	def connect(self):
		if not self.conn:
			if self.tls:
				self.conn = http.client.HTTPSConnection(self.host)
			else:
				self.conn = http.client.HTTPConnection(self.host)

	def disconnect(self):
		if self.conn:
			self.conn.close()
			self.conn = None

	def getPrice(self, orderCode):
		raise NotImplementedError

	def getPrices(self, orderCodes):
		for orderCode in orderCodes:
			try:
				yield self.getPrice(orderCode)
			except self.Error as e:
				raise "Error while processing %s '%s':\n%s" % (
					self.supplierName, orderCode, str(e))