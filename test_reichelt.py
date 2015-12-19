#!/usr/bin/env python3

from partmgr.pricefetch import *

fetcher = PriceFetcher.get("reichelt")()
orderCodes = ("RAD 1/63",
	      "RAD 1/42",
	      " RAD 1.000/63 ")
for res in fetcher.getPrices(orderCodes):
	print(res)
