from partmgr_tstlib import *
from partmgr.pricefetch import *

class Test_Pricefetch(TestCase):
	def test_reichelt(self):
		testData = (
			("RAD 1/63", PriceFetcher.Result.FOUND),
			("RAD 1/42", PriceFetcher.Result.NOTFOUND),
			(" RAD 1.000/63 ", PriceFetcher.Result.FOUND),
		)
		self.__runPriceFetchTest("reichelt", testData)

	@unittest.skip("Conrad fetcher is currently broken")
	def test_conrad(self):
		testData = (
			("405132 - 62", PriceFetcher.Result.FOUND),
			("405132", PriceFetcher.Result.FOUND),
			("9999999 - 99", PriceFetcher.Result.NOTFOUND),
			("9999999", PriceFetcher.Result.NOTFOUND),
			("405191", PriceFetcher.Result.FOUND),
			("405191 - 62", PriceFetcher.Result.FOUND),
			("408042 - 62", PriceFetcher.Result.FOUND),
			("408042", PriceFetcher.Result.FOUND),
		)
		self.__runPriceFetchTest("conrad", testData)

	@unittest.skip("Pollin fetcher is currently broken")
	def test_pollin(self):
		testData = (
			("702 737", PriceFetcher.Result.FOUND),
			("94-702737", PriceFetcher.Result.FOUND),
			(" 94-702 737 ", PriceFetcher.Result.FOUND),
			("99-999 999", PriceFetcher.Result.NOTFOUND),
			("000 000", PriceFetcher.Result.NOTFOUND),
			("94-702 737", PriceFetcher.Result.FOUND),
			("711 677", PriceFetcher.Result.FOUND),
		)
		self.__runPriceFetchTest("pollin", testData)

	def __runPriceFetchTest(self, name, testData):
		fetcher = PriceFetcher.get(name)()
		for i, res in enumerate(fetcher.getPrices(d[0] for d in testData)):
			print(f"getPrices() result: {res}")
			orderCode, expectedStatus = testData[i]
			self.assertEqual(res.status, expectedStatus)
			self.assertEqual(res.orderCode, orderCode.strip())
			if expectedStatus == PriceFetcher.Result.FOUND:
				self.assertTrue(res.price > 0.0)
			self.assertEqual(res.currency, Param_Currency.CURR_EUR)
