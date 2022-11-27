# -*- coding: utf-8 -*-
#
# PartMgr - Price fetching
#
# Copyright 2015-2022 Michael Buesch <m@bues.ch>
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


class PriceFetcher:
	"""Part price fetcher."""

	class Error(Exception):
		pass

	class Result:
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

	supplierNames = None
	host = None

	_registeredFetchers = []

	_defaultHttpHeaders = {
		"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
		"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language" : "*",
		"Accept-Charset" : "utf-8,*;q=0.9",
	}

	@classmethod
	def register(cls):
		PriceFetcher._registeredFetchers.append(cls)

	@classmethod
	def get(cls, wantedSupplierName):
		stripCs = "/\\_-,.;:\"'()|"
		wantedSupplierName = wantedSupplierName.lower().strip().strip(stripCs).strip()
		for fetcher in cls._registeredFetchers:
			if wantedSupplierName in (n.lower().strip().strip(stripCs).strip()
						  for n in fetcher.supplierNames):
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

	def _relax(self):
		pass

	def _sendRequest(self, method, url, body=None, headers={}):
		if not headers:
			headers = self._defaultHttpHeaders
		self.conn.request(method, url, body, headers)
		self._relax()

	def _getResponse(self, withHeaders = False):
		self._relax()
		response = self.conn.getresponse()
		self._relax()
		data = response.read()
		self._relax()
		if withHeaders:
			return data, response.getheaders()
		return data

	def connect(self):
		if not self.conn:
			try:
				if self.tls:
					self.conn = http.client.HTTPSConnection(self.host)
				else:
					self.conn = http.client.HTTPConnection(self.host)
			except http.client.HTTPException as e:
				raise self.Error("Error while connecting to %s:\n%s" % (
					self.supplierNames[0], str(e)))

	def disconnect(self):
		if self.conn:
			try:
				self.conn.close()
			except http.client.HTTPException as e:
				pass
			self.conn = None

	def _getPrice(self, orderCode):
		raise NotImplementedError

	def getPrices(self, orderCodes,
		      preCallback=None,
		      postCallback=None):
		for orderCode in orderCodes:
			tries = 0
			while 1:
				tries += 1
				try:
					if preCallback:
						preCallback(orderCode)
					yield self._getPrice(orderCode)
					if postCallback:
						postCallback(orderCode)
				except http.client.HTTPException as e:
					if tries < 5:
						print("Price fetch %s '%s' failed. Retrying..." % (
						      self.supplierNames[0], orderCode))
						self.disconnect()
						continue
					raise self.Error("Error while processing %s '%s':\n%s" % (
						self.supplierNames[0], orderCode, str(e)))
				except self.Error as e:
					raise self.Error("Error while processing %s '%s':\n%s" % (
						self.supplierNames[0], orderCode, str(e)))
				break
