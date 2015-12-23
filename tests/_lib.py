from partmgr.pricefetch import *
import re

def priceFetchTest(name, testData):
	fetcher = PriceFetcher.get(name)()
	for i, res in enumerate(fetcher.getPrices(d[0] for d in testData)):
		print(res)
		orderCode, expectedStatus = testData[i]
		assert(res.orderCode == orderCode.strip())
		if expectedStatus == PriceFetcher.Result.FOUND:
			assert(res.price > 0.0)
		assert(res.status == expectedStatus)
		assert(res.currency == Param_Currency.CURR_EUR)
