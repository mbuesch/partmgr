from tests._lib import *

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
priceFetchTest("conrad", testData)
