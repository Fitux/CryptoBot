from Exchanger import Exchanger
from bittrex.bittrex import Bittrex, API_V1_1, BUY_ORDERBOOK, SELL_ORDERBOOK 

class BittrexExchanger(Exchanger):
	__bittrex = None

	def __init__(self, key, secret):
		self.__apiKey = key
		self.__apiSecret = secret
		self.__apiVersion = API_V1_1

		self.__bittrex = Bittrex(self.__apiKey, self.__apiSecret, api_version=self.__apiVersion)

	def __getMarketsList(self):
		data = self.__bittrex.get_markets()
		result = []

		for market in data["result"]:
			if(market["MarketName"] not in result and market["IsActive"]):
				result.append(market["MarketName"])

		return result

	def __getCurrenciesList(self):
		data = self.__bittrex.get_currencies()

		result = []

		for currency in data["result"]:
			if(currency["Currency"] not in result and currency["IsActive"]):
				result.append(currency["Currency"])

		return result

	def __getLastPrice(self, market):
		data = self.__bittrex.get_ticker(market)
		result = data["result"]
		return result["Last"]

	def getMarkets(self):
		data = self.__bittrex.get_markets()
		return data["result"]

	def getCurrencies(self):
		data = self.__bittrex.get_currencies()
		return data["result"]

	def getTicker(self, market):
		data = self.__bittrex.get_ticker(market)
		return data["result"]

	def getBothOrderBook(self, market):
		data = self.__bittrex.get_orderbook(market)
		return data["result"]

	def getBuyOrderBook(self, market):
		data = self.__bittrex.get_orderbook(market, depth_type=BUY_ORDERBOOK)
		return data["result"]

	def getSellOrderBook(self, market):
		data = self.__bittrex.get_orderbook(market, depth_type=SELL_ORDERBOOK)
		return data["result"]

	def getMarketSummaries(self):
		data = self.__bittrex.get_market_summaries()
		return data["result"]

	def getMarketSummary(self, market):
		data = self.__bittrex.get_market_summary(market)
		return data["result"]

	def getMarketHistory(self, market):
		data = self.__bittrex.get_market_history(market)
		return data["result"]