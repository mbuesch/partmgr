from tests._lib import *

testData = (
	("702 737", PriceFetcher.Result.FOUND),
	("94-702737", PriceFetcher.Result.FOUND),
	(" 94-702 737 ", PriceFetcher.Result.FOUND),
	("99-999 999", PriceFetcher.Result.NOTFOUND),
	("000 000", PriceFetcher.Result.NOTFOUND),
	("94-702 737", PriceFetcher.Result.FOUND),
	("711 677", PriceFetcher.Result.FOUND),
)
priceFetchTest("pollin", testData)
