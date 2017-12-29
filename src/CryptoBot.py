# Datetime import is needed since we are going to use the time to avoid 
# doing a lot of request in a small amout of time
import datetime;

# Enum es used for the FiatCurrencies enumaration used that is still being implemented
from enum import Enum
# Importing the coinmarketcap api that will let us get all the info needed for reporting
from coinmarketcap import Market
# Chat bot is the father class we are using to implement out own cryptoBot
from chatBot.ChatBot import ChatBot, BotState

# This may not be needed, just added in case we may use an enum instead of string
# This is just a prototype idea of redisigning the use of the fiat currency
class FiatCurrencies(Enum):
	__order__ = 'USD AUD BRL CAD CHF CNY EUR GBP HKD IDR INR JPY KRW MXN RUB'
	USD = 'usd'
	AUD = 'aud'
	BRL = 'brl'
	CAD = 'cad'
	CHF = 'chf'
	CNY = 'cny'
	EUR = 'eur'
	GBP = 'gbp'
	HKD = 'hkd'
	IDR = 'idr'
	INR = 'inr'
	JPY = 'jpy'
	KRW = 'krw'
	MXN = 'mxn'
	RUB = 'rub'

# This class will be in charge of expanding the Chatbot class with new features
# This class will implement the coinmarketcap api to expand the functionality
class CryptoBot(ChatBot):
	# All the variables related to the new functionalities implemented by the class cryptoBot
	# __defaultCoin is used to know which will be the coin used to report the value of other coins
	# __defaultCurrency is used to know which of the fiat currency is going to be used for reporting
	# __supportedCurrencies will be the list of currencies that coinmarketcap supports in their api
	# __savedStats is where we are going to store all the information about the main stats in the market
	# __savedTickers is where we are going to store all the information related to the coins based on their currency
	# __currencyPerson is where we will store if someone changes their currency and which are they going to use
	# __lastUpdatedStats is the timestamp of the last update in the stats
	# __lastUpdatedTickers is the timestamp of the last update in the tickers
	# __updateInterval is the value in seconds of the minimum amount of time needed to update the stats and tickers again
	__defaultCoin = "BTC"
	__defaultCurrency = "USD"
	__supportedCurrencies = ["USD", "AUD", "BRL", "CAD", "CHF", "CNY", "EUR", "GBP", "HKD", "IDR", "INR", "JPY", "KRW", "MXN", "RUB"]
	__savedStats = {}
	__savedTickers = {}
	__currencyPerson = {}
	__lastUpdatedStats = {}
	__lastUpdatedTickers = {}
	__updateInterval = None

	# __coinMarketCap is the object created by the coinMarketCap api that will get us all the information from them
	__coinMarketCap = None
	# __exchangerList is the list of exchanger objects that we will use for the functionalities related to the exchangers
	__exchangerList = None


	# Setup of all variables
	def __init__(self, token, superadminid, adminsid=[], exchangers=[], updateInterval = 300):
		super(CryptoBot, self).__init__(token, superadminid, adminsid)

		self.__exchangerList = exchangers
		self.__updateInterval = updateInterval		

		self.__coinmarketcap = Market()

		for currency in self.__supportedCurrencies:
			self.__lastUpdatedStats[currency] = datetime.datetime.min
			self.__lastUpdatedTickers[currency] = datetime.datetime.min
			self.__getStats(currency)
			self.__getTickers(currency)

		return

	# Functions related to bot functionalities with especific exchangers

	# It will add a new exchanger object to the list of exchangers we already have
	def addExchanger(self, exchanger):
		raise NotImplementedError("You need to implement addExchanger before using it")

	# It will remove an exchanger object from the list of exchangers we have
	def removeExchanger(self, exchanger):
		raise NotImplementedError("You need to implement removeExchanger before using it")

	# Function to change the interval between updates
	def setUpdateInterval(self, interval):
		self.__updateInterval = interval

	# Function to get the interval between updates
	def getUpdateInterval(self):
		return self.__updateInterval

	# Related to bot functiuonalities with any info in the coins

	# Function that will create an alarm in case of a coin prices goes above the price we set
	def setAlertPriceAbove(self, coin, price, person):
		raise NotImplementedError("You need to implement setAlertPriceAbove before using it")

	# Function that will create an alarm in case of a coin prices goes below the price we set
	def setAlertPriceBelow(self, coin, price, person):
		raise NotImplementedError("You need to implement setAlertPriceBelow before using it")

	# Function that will remove an alarm
	def removeAlert(self, alertid, person):
		raise NotImplementedError("You need to implement removeAlert before using it")
	
	# Information related to coins
	# This function will get all the info related to a coin
	def getInfo(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency

		tickers = self.__getTickers(currency)
		
		coin = coin.upper()
		for ticker in tickers:
			if(ticker['symbol'].upper() == coin or ticker['name'].upper() == coin or ticker['id'].upper() == coin):
				coinTicker = ticker

		return coinTicker

	# The function that will return the price in fiat of certain coin
	def getPriceInFiat(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency

		coinTicker = self.getInfo(coin,currency)
		keyPrice = "price_" + currency.lower()

		return coinTicker[keyPrice]

	# The function that will return the price in btc of certain coin
	def getPriceInCoin(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)
		keyPrice = "price_" + self.__defaultCoin.lower()

		return coinTicker[keyPrice]

	# The function that will return the market cap of certain coin
	def getMarketCap(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)
		keyMarketCap = "market_cap_" + currency.lower()

		return coinTicker[keyMarketCap]

	# The function that will return the last 24h volume of certain coin
	def getVolume(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)
		keyVolume = "24h_volume_" + currency.lower()

		return coinTicker[keyVolume]

	# The function that will return the change in price of the last 24h of certain coin
	def getChangeLastDay(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)
		keyChange = "percent_change_24h"

		return coinTicker[keyChange]

	# The function that will return the change in price of the last 1h of certain coin
	def getChangeLastHour(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)
		keyChange = "percent_change_1h"

		return coinTicker[keyChange]

	# The function that will return the change in price of the last 7d of certain coin
	def getChangeLastSevenDays(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)
		keyChange = "percent_change_7d"

		return coinTicker[keyChange]

	# Coinmarketcap function wrapper that will helps us to avoid doing a lot of request to get the stats
	def __getStats(self, currency):
		currentTime = datetime.datetime.now()
		lapsedTime = (currentTime - self.__lastUpdatedStats[currency]).total_seconds()

		if(lapsedTime > self.__updateInterval):
			self.__lastUpdatedStats[currency] = currentTime
			if(currency != self.__defaultCurrency and currency in self.__supportedCurrencies):
				self.__savedStats[currency] = self.__coinmarketcap.stats(convert=currency)
			else:
				self.__savedStats[currency] = self.__coinmarketcap.stats()

		return self.__savedStats[currency]

	# Coinmarketcap function wrapper that will helps us to avoid doing a lot of request to get the tickers
	def __getTickers(self, currency):
		currentTime = datetime.datetime.now()
		lapsedTime = (currentTime - self.__lastUpdatedTickers[currency]).total_seconds()

		if(lapsedTime > self.__updateInterval):
			self.__lastUpdatedTickers[currency] = currentTime
			if(currency != self.__defaultCurrency):
				self.__savedTickers[currency] = self.__coinmarketcap.ticker(convert=currency)
			else:
				self.__savedTickers[currency] = self.__coinmarketcap.ticker()

		return self.__savedTickers[currency]
			