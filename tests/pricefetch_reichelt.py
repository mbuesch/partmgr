from tests._lib import *

testData = (
	("RAD 1/63", PriceFetcher.Result.FOUND),
	("RAD 1/42", PriceFetcher.Result.NOTFOUND),
	(" RAD 1.000/63 ", PriceFetcher.Result.FOUND),
)
priceFetchTest("reichelt", testData)
