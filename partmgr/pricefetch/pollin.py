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


class PollinPriceFetcher(PriceFetcher):
	supplierNames = ("Pollin",
			 "pollin.de",
			 "www.pollin.de",)
	host = "www.pollin.de"

	def __init__(self, tls = True):
		self.__sid = None
		PriceFetcher.__init__(self, tls = tls)

	def __getSessionId(self):
		for i in range(5):
			self._sendRequest("GET", "/shop/warenkorb.html")
			data, hdrs = self._getResponse(withHeaders = True)
			for hdr, value in hdrs:
				if hdr.lower().strip() == "set-cookie":
					m = re.match(r'PHPSESSID=(\w+).*',
						     value, re.DOTALL)
					if m:
						return m.group(1)
			time.sleep(0.2)
		raise self.Error("Failed to get Pollin session ID.")

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
			raise self.Error("Invalid empty Pollin order code.")
		codes = orderCode.split("-")
		if len(codes) == 1:
			wkz, bestellnr = "", codes[0]
		elif len(codes) == 2:
			wkz, bestellnr = codes
		else:
			raise self.Error("Invalid Pollin part number format "
					 "(must be  00-000 000  or  000 000)")
		wkz = re.sub(r'\s', "", wkz)
		bestellnr = re.sub(r'\s', "", bestellnr)

		header = self._defaultHttpHeaders.copy()
		header["Cookie"] = "PHPSESSID=" + self.__sid + "; pollincookie=1"
		header["Content-Type"] = "application/x-www-form-urlencoded"

		# Add the item to the basket
		body = urllib.parse.urlencode(
			(("do_anzahl_0", "1"),
			 ("do_wkz_0", wkz),
			 ("do_bestellnr2_0", bestellnr)),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", "/shop/warenkorb.html", body, header)
		basket = self._getResponse().decode("UTF-8", "ignore")

		# Remove the item from the basket.
		body = urllib.parse.urlencode(
			(("action", "delete"),
			 ("doAction", ""),
			 ("wkChk[00%s]" % bestellnr, "on"),
			 ("wk_anzahl_0", "1"),
			 ("gsn", "")),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", "/shop/warenkorb.html", body, header)
		self._getResponse()

		# Extract the price from the basket.
		m = re.match(r'.*'
			     r'<td class="articleAvailability">\s*'
			     r'<img src="/shop/images/spacer.gif"\s+'
			     r'alt="[\w\s&;äöüÄÖÜ\-]+"\s*/>\s*'
			     r'</td>\s*'
			     r'<td>\s*'
			     r'(\d+,\d+)\s+&euro;\s*'
			     r'</td>\s*'
			     r'.*',
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

#PollinPriceFetcher.register()
