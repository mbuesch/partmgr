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

from partmgr.pricefetch.pricefetch import *

import re
import time


class ConradPriceFetcher(PriceFetcher):
	supplierNames = ("Conrad",
			 "conrad.de",
			 "www.conrad.de",)
	host = "www.conrad.de"

	def __init__(self, tls = True):
		self.__sid = None
		PriceFetcher.__init__(self, tls = tls)

	def __getSessionId(self):
		for i in range(5):
			self._sendRequest("GET", "/de.datalayer.json/content/"
						 "conrad-de/b2c/de?_=1450942424242")
			data, hdrs = self._getResponse(withHeaders = True)
			for hdr, value in hdrs:
				if hdr.lower().strip() == "set-cookie":
					m = re.match(r'sessionid=(\w+).*',
						     value, re.DOTALL)
					if m:
						return m.group(1)
			time.sleep(0.2)
		raise self.Error("Failed to get Conrad session ID.")

	def connect(self):
		if not self.conn:
			PriceFetcher.connect(self)
			self.__sid = self.__getSessionId()

	def disconnect(self):
		if self.conn:
			self.__sid = None
			PriceFetcher.disconnect(self)

	def _getPrice(self, orderCode):
		self.connect()

		orderCode = orderCode.strip()
		if not orderCode:
			raise self.Error("Invalid empty Conrad order code.")
		code = orderCode.split("-")
		if len(code) == 1:
			productCode, productCodeFlag = code[0], ""
		elif len(code) == 2:
			productCode, productCodeFlag = code
		else:
			raise self.Error("Invalid Conrad part number format "
					 "(must be  0000000-00  or  0000000)")
		productCode = re.sub(r'\s', "", productCode)
		productCodeFlag = re.sub(r'\s', "", productCodeFlag)

		header = self._defaultHttpHeaders.copy()
		header["Cookie"] = "sessionid=" + self.__sid

		# Add the item to the basket
		body = urllib.parse.urlencode(
			(("redirect", "/de/cart.html"),
			 ("redirect-product-not-found", "/de/cart.html"),
			 ("productCode-0", productCode),
			 ("productCodeFlag-0", productCodeFlag),
			 ("productQuantity-0", "1")),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Type"] = "application/x-www-form-urlencoded"
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", "/de/cart.addcartentry.html", body, header)
		self._getResponse()

		# Fetch the basket
		header.pop("Content-Type")
		header.pop("Content-Length")
		self._sendRequest("GET", "/de/cart.html", None, header)
		basket = self._getResponse().decode("UTF-8", "ignore")

		# Extract the entry ID
		m = re.match(r'.*<input type="hidden" name="entryId" value="([\w\-]+)"/>.*',
			     basket, re.DOTALL)
		if not m:
			return self.Result(orderCode = orderCode,
					   status = self.Result.NOTFOUND)
		entryId = m.group(1)

		# Remove the item from the basket.
		body = urllib.parse.urlencode(
			(("redirect", "/de/cart.html"),
			 ("entryId", entryId)),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Type"] = "application/x-www-form-urlencoded"
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", "/de/cart.removecartentry.html", body, header)
		self._getResponse()

		# Extract the price from the basket.
		m = re.match(r'.*<div\sclass="ccpProductListCartItem__price">(\d+,\d+)\s.*',
			     basket, re.DOTALL)
		if not m:
			return self.Result(orderCode = orderCode,
					   status = self.Result.NOTFOUND)
		price = m.group(1)
		try:
			price = float(price.replace(",", "."))
			if price <= 0.0:
				raise ValueError
		except ValueError as e:
			return self.Result(orderCode = orderCode,
					   status = self.Result.NOTFOUND)

		return self.Result(orderCode = orderCode,
				   price = price)

#ConradPriceFetcher.register()
