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


class ReicheltPriceFetcher(PriceFetcher):
	supplierNames = ("Reichelt",
			 "reichelt.de",
			 "www.reichelt.de",
			 "secure.reichelt.de",)

	def __init__(self, tls = True):
		if tls:
			self.host = "secure.reichelt.de"
		else:
			self.host = "www.reichelt.de"
		self.__sid = None
		PriceFetcher.__init__(self, tls = tls)

	def __getSessionId(self):
		for i in range(5):
			self._sendRequest("GET", "/")
			resp = self._getResponse().decode(
					"UTF-8", "ignore")
			m = re.match(r'.*SID=(\w{53,53}).*', resp, re.DOTALL)
			if m:
				break
			time.sleep(0.2)
		else:
			raise self.Error("Failed to get Reichelt session ID.")
		return m.group(1)

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
			raise self.Error("Invalid empty Reichelt order code.")

		postUrl = "/Warenkorb/5/index.html?" \
			  "&ACTION=5&LA=0;SID=" + self.__sid

		header = self._defaultHttpHeaders.copy()
		header["Content-Type"] = "application/x-www-form-urlencoded"

		# Add the item to the basket
		body = urllib.parse.urlencode(
			(("DirectInput_[1]", orderCode),
			 ("DirectInput_count_[1]", "1")),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", postUrl, body, header)
		basket = self._getResponse().decode("UTF-8", "ignore")

		# Remove the item from the basket.
		body = urllib.parse.urlencode(
			(("Delete[_all_]", "WK löschen"),),
			encoding = "UTF-8",
			errors = "ignore")
		header["Content-Length"] = str(len(body))
		self._sendRequest("POST", postUrl, body, header)
		self._getResponse()

		# Extract the price from the basket.
		m = re.match(r'.*<span class="tablet einzelpreis">Einzelpreis</span>'
			     r'(?:\s*<s class="streichpreis"><span>\d+,\d+</span>&nbsp;&euro;</s>\s*)?'
			     r'<span>(\d+,\d+)</span>.*',
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

ReicheltPriceFetcher.register()
