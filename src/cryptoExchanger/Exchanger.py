from abc import ABCMeta, abstractmethod

# Class definition of exchanger objects that will be used by the bot
# It will be class that all the wrappers for exchangers need to use
# All of them should return the same information
# Right now the only wrapper that will be created will be Bittrex
class Exchanger(object):
	__metaclass__ = ABCMeta
	__apiKey = None
	__apiSecret = None
	__apiVersion = None

	@abstractmethod
	def getMarkets(self):
		pass

	@abstractmethod
	def getCurrencies(self):
		pass

	@abstractmethod
	def getBuyOrderBook(self, market):
		pass

	@abstractmethod
	def getSellOrderBook(self, market):
		pass

	@abstractmethod
	def getBothOrderBook(self, market):
		pass

	@abstractmethod
	def getMarketSummaries(self):
		pass

	@abstractmethod
	def getMarketSummary(self, market):
		pass

	@abstractmethod
	def getMarketHistory(self, market):
		pass

	@abstractmethod
	def placeBuyOrder(self, market, ordertype, quantity, rate):
		pass

	@abstractmethod
	def placeSellOrder(self, market, ordertype, quantity, rate):
		pass

	@abstractmethod
	def cancelOrder(self, orderid):
		pass

	@abstractmethod
	def getOpenOrders(self, market=None):
		pass

	@abstractmethod
	def getBalance(self, currency):
		pass

	@abstractmethod
	def getBalances(self):
		pass

	@abstractmethod
	def getOrderInfo(self, orderid):
		pass