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

# Class to be able to identify the different type of fields for a coin information
class CoinField(Enum):
	NAME = 'name'
	SYMBOL = 'symbol'
	RANK = 'rank'
	PRICE_COIN = 'price_coin'
	PRICE_FIAT = 'price_fiat'
	MARKET_CAP = 'market_cap'
	VOLUME = 'volume'
	CHANGE_1H = 'percent_1h'
	CHANGE_24H = 'percent_24h'
	CHANGE_7D = 'percent_7d'

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
	def __init__(self, token, superadminid, adminsid=[], exchangers=[], updateInterval=300, debuglevel=0):
		super(CryptoBot, self).__init__(token, superadminid, adminsid, debuglevel)
		self._debugLevel = debuglevel
		if (self._debugLevel > 0): print "Debug Level: " + str(debuglevel)

		self.__exchangerList = exchangers
		self.__updateInterval = updateInterval	
		if (self._debugLevel >= 1): print "Update Interval: " + str(updateInterval)

		self.__coinmarketcap = Market()

		for currency in self.__supportedCurrencies:
			if (self._debugLevel >= 1): print "Supported Currency: " + currency
			self.__lastUpdatedStats[currency] = datetime.datetime.min
			self.__lastUpdatedTickers[currency] = datetime.datetime.min
			self.__getStats(currency)
			self.__getTickers(currency)

		if (self._debugLevel >= 1): print "Adding Handlers"
		self._addCommandHandler('currency', self.__setCurrency, pass_args=True)
		self._addCommandHandler('fiatPrice', self.__getPriceFiat, pass_args=True)
		self._addCommandHandler('price', self.__getPriceCoin, pass_args=True)
		self._addCommandHandler('rank', self.__getRank, pass_args=True)
		self._addCommandHandler('marketcap', self.__getMarketCap, pass_args=True)
		self._addCommandHandler('volume', self.__getVolume, pass_args=True)
		self._addCommandHandler('change1h', self.__getChangeLastHour, pass_args=True)
		self._addCommandHandler('change24h', self.__getChangeLastDay, pass_args=True)
		self._addCommandHandler('change7d', self.__getChangeLastSevenDays, pass_args=True)
		self._addCommandHandler('coinInfo', self.__getInfoCoin, pass_args=True)

		self._removeHandler(self._unknownHandler)
		self._addHandler(self._unknownHandler)

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

	# Function to set an specific user currency
	def setUserCurrency(self, userid, currency):
		self.__currencyPerson[userid] = currency

	# Function to get a user currency settings
	def getUserCurrency(self, userid):
		return self.__currencyPerson.get(userid) or self.__defaultCurrency

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
	def getStringInfo(self, coins, currency=None, field=None):
		if(currency == None):
			currency = self.__defaultCurrency

		infoString = ""

		if (self._debugLevel >= 1): print "Getting String Info"
		if (self._debugLevel >= 2): print "Field: " + field
		if (self._debugLevel >= 2): print "Coins: " + str(coins)

		for coin in coins:
			info = self.getInfo(coin, currency)
			priceInFiat = self.getPriceInFiat(coin, currency)
			priceInCoin = self.getPriceInCoin(coin)
			marketCap = self.getMarketCap(coin, currency)
			volume = self.getVolume(coin, currency)
			change1h = self.getChangeLastHour(coin)
			change24h = self.getChangeLastDay(coin)
			change7d = self.getChangeLastSevenDays(coin)

			if (self._debugLevel >= 2): print "Info: " + str(info)

			if(info != None):
				infoString += "Name of coin: " + info['name'] + " [" + info['symbol'] + "]\n"

				if(field == None):
					infoString += "Rank: " + info['rank'] + "\n\n"
					infoString += "Price in " + currency + ": " + priceInFiat + "\n"
					infoString += "Price in " + self.__defaultCoin + ": " + priceInCoin + "\n\n"
					infoString += "Market Cap in " + currency + ": " + marketCap + "\n"
					infoString += "24h Volume in " + currency + ": " + volume + "\n\n"
					infoString += "Change 1h: " + change1h + "\n"
					infoString += "Change 24h: " + change24h + "\n"
					infoString += "Change 7d: " + change7d + "\n\n"
				elif (field == CoinField.PRICE_FIAT):
					infoString += "Price in " + currency + ": " + priceInFiat + "\n\n"
				elif (field == CoinField.PRICE_COIN):
					infoString += "Price in " + self.__defaultCoin + ": " + priceInCoin + "\n\n"
				elif (field == CoinField.MARKET_CAP):
					infoString += "Market Cap in " + currency + ": " + marketCap + "\n\n"
				elif (field == CoinField.VOLUME):
					infoString += "24h Volume in " + currency + ": " + volume + "\n\n"
				elif (field == CoinField.CHANGE_1H):
					infoString += "Change 1h: " + change1h + "\n\n"
				elif (field == CoinField.CHANGE_24H):
					infoString += "Change 24h: " + change24h + "\n\n"
				elif (field == CoinField.CHANGE_7D):
					infoString += "Change 7d: " + change7d + "\n\n"
				elif (field == CoinField.RANK):
					infoString += "Rank: " + info['rank'] + "\n\n"
		
		if (self._debugLevel >= 2): print "String Info: \n" + infoString
		return infoString

	# This function will get all the info related to a coin
	def getInfo(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency

		coinTicker = None
		tickers = self.__getTickers(currency)
		
		coin = coin.upper()
		for ticker in tickers:
			if(ticker['symbol'].upper() == coin or ticker['name'].upper() == coin or ticker['id'].upper() == coin):
				coinTicker = ticker

		if (self._debugLevel >= 3): print "Info: " + str(coinTicker)
		return coinTicker

	# The function that will return the price in fiat of certain coin
	def getRank(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyRank = "rank"

		if (self._debugLevel >= 2): print "Rank: " + coinTicker[keyRank]
		return coinTicker[keyRank]

	# The function that will return the price in fiat of certain coin
	def getPriceInFiat(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency

		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyPrice = "price_" + currency.lower()

		if (self._debugLevel >= 2): print "PriceFiat: " + coinTicker[keyPrice]
		return coinTicker[keyPrice]

	# The function that will return the price in btc of certain coin
	def getPriceInCoin(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyPrice = "price_" + self.__defaultCoin.lower()

		if (self._debugLevel >= 2): print "PriceCoin: " + coinTicker[keyPrice]
		return coinTicker[keyPrice]

	# The function that will return the market cap of certain coin
	def getMarketCap(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyMarketCap = "market_cap_" + currency.lower()

		if (self._debugLevel >= 2): print "Market Cap: " + coinTicker[keyMarketCap]
		return coinTicker[keyMarketCap]

	# The function that will return the last 24h volume of certain coin
	def getVolume(self, coin, currency=None):
		if(currency == None):
			currency = self.__defaultCurrency
		
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyVolume = "24h_volume_" + currency.lower()

		if (self._debugLevel >= 2): print "Volume: " + coinTicker[keyVolume]
		return coinTicker[keyVolume]

	# The function that will return the change in price of the last 24h of certain coin
	def getChangeLastDay(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyChange = "percent_change_24h"

		if (self._debugLevel >= 2): print "Change 24h: " + coinTicker[keyChange]
		return coinTicker[keyChange]

	# The function that will return the change in price of the last 1h of certain coin
	def getChangeLastHour(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyChange = "percent_change_1h"

		if (self._debugLevel >= 2): print "Change 1h: " + coinTicker[keyChange]
		return coinTicker[keyChange]

	# The function that will return the change in price of the last 7d of certain coin
	def getChangeLastSevenDays(self, coin):
		currency = self.__defaultCurrency
		coinTicker = self.getInfo(coin,currency)

		if(coinTicker == None):
			return None

		keyChange = "percent_change_7d"

		if (self._debugLevel >= 2): print "Change 7d: " + coinTicker[keyChange]
		return coinTicker[keyChange]

	# Coinmarketcap function wrapper that will helps us to avoid doing a lot of request to get the stats
	def __getStats(self, currency):
		currentTime = datetime.datetime.now()
		lapsedTime = (currentTime - self.__lastUpdatedStats[currency]).total_seconds()

		if(lapsedTime > self.__updateInterval):
			if (self._debugLevel >= 1): print "Updating Stats for: " + currency
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
			if (self._debugLevel >= 1): print "Updating Ticker for: " + currency
			self.__lastUpdatedTickers[currency] = currentTime
			if(currency != self.__defaultCurrency):
				self.__savedTickers[currency] = self.__coinmarketcap.ticker(convert=currency)
			else:
				self.__savedTickers[currency] = self.__coinmarketcap.ticker()

		return self.__savedTickers[currency]
			
	# Callback functions that the bot will call after receiving a command
	def __setCurrency(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)

		if (self._debugLevel >= 1): print "Set Currency command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		for currency in args:
			if (self._debugLevel >= 2): print "Arg: " + currency
			if(currency in self.__supportedCurrencies):
				self.setUserCurrency(userId, currency)
				returningMessage = "Your currency now was set to " + currency

		if (self._debugLevel >= 1): print "Currency for user " + userId + " set to: " + currency

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getRank(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.RANK

		if (self._debugLevel >= 1): print "Get Rank command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getPriceFiat(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.PRICE_FIAT

		if (self._debugLevel >= 1): print "Get Price Fiat command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getPriceCoin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.PRICE_COIN

		if (self._debugLevel >= 1): print "Get Price Coin command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getMarketCap(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.MARKET_CAP

		if (self._debugLevel >= 1): print "Get Market Cap coomand"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getVolume(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.VOLUME

		if (self._debugLevel >= 1): print "Get Volume command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getChangeLastDay(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.CHANGE_24H

		if (self._debugLevel >= 1): print "Get Change 24h command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getChangeLastHour(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.CHANGE_1H

		if (self._debugLevel >= 1): print "Get Change 1h command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getChangeLastSevenDays(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)
		field = CoinField.CHANGE_7D

		if (self._debugLevel >= 1): print "Get Change 7d command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency, field)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getInfoCoin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		currency = self.__currencyPerson.get(userId)

		if (self._debugLevel >= 1): print "Get Info command"
		if (self._debugLevel >= 2): print "Args: " + str(args)

		returningMessage = self.getStringInfo(args, currency)

		bot.send_message(chat_id=chatId, text=returningMessage)

		return 
