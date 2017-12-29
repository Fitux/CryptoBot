# This is the current implementation of the chat bot
# Right now it will work only in telegram
# This bot will have 2 type of actions (functions)
# The first type will be related to the bot functioning, to make sure it works as a bot (Should be able to get messages, be able to read them, etc)
# Second type will be related to its usage, to make sure the bot works depending on the user actions (Should interact correctly to the first actions)
# The main actions this bot should do are the following:
# -Have a couple of basic commands (start, stop, resume, sleep)
# -Be able to receive commands and answer them
# -Only admins should be able to execute the basic commands
# -Be able to add or remove admins (It will have just 1 super admin that shouldn't be removed)
# 
# We should be able to start or stop the polling of the messages (Those won't be bot actions)

from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram.ext import MessageHandler, Filters
from enum import Enum

class BotState(Enum):
	DEACTIVATED = 0
	ACTIVATED = 1
	SLEEPING = 2

class ChatBot(object):
	# Declaration of all variables
	# The __currentState will be based on the BotState Enum implementation
	# The __accessToken is the identifier needed for the bot to connect
	# The __botSuperAdmin is the administrator that shouldn't be removed by any circunstances
	# The __botAdmins are the other administrators that can execute the bot commands
	# The __isPolling is a flag that will let us know if the bot is polling for messages
	# The __botUpdater is the one in charge of update the chatbot and contains the dispatcher
	# The __botDispatcher is the one in charge of call the correct handlers used by the messages
	__isPolling = None
	__currentState = None
	__accessToken = None
	__botUpdater = None
	__botDispatcher = None
	__botHandlers = []
	__botAdmins = []
	__botSuperAdmin = None

	def __init__(self, token, superadminid, adminsid=[]):
		# Defining the basic variables needed to work
		# The __currentState will be based on the BotState Enum implementation
		# The __accessToken is the identifier needed for the bot to connect
		# The __botSuperAdmin is the administrator that shouldn't be removed by any circunstances
		# The __botAdmins are the other administrators that can execute the bot commands

		self.__currentState = BotState.DEACTIVATED
		self.__accessToken = token
		self.__botSuperAdmin = superadminid
		self.__botAdmins.append (superadminid)

		for personid in adminsid:
			if(personid not in self.__botAdmins):
				self.__botAdmins.append (personid)

		# The __isPolling is a flag that will let us know if the bot is polling for messages
		# The __botUpdater is the one in charge of update the chatbot and contains the dispatcher
		# The __botDispatcher is the one in charge of call the correct handlers used by the messages
		self.__isPolling = False
		self.__botUpdater = Updater(token=self.__accessToken)
		self.__botDispatcher = self.__botUpdater.dispatcher

		# Here we will add all the basic handlers needed for the chat bot
		self.__botHandlers.append (CommandHandler('startBot', self.__startBot))
		self.__botHandlers.append (CommandHandler('stopBot', self.__stopBot))
		self.__botHandlers.append (CommandHandler('resumeBot', self.__resumeBot))
		self.__botHandlers.append (CommandHandler('sleepBot', self.__sleepBot))
		self.__botHandlers.append (CommandHandler('listAdmins', self.__listAdmins))
		self.__botHandlers.append (CommandHandler('removeAdmin', self.__removeAdmin, pass_args=True))
		self.__botHandlers.append (CommandHandler('addAdmin', self.__addAdmin, pass_args=True))
		self.__botHandlers.append (CommandHandler('myUserId', self.__getUserId))
		self.__botHandlers.append (CommandHandler('botState', self.__getCurrentState))

		# This should be always the last handler added so will be only used when it does not recognize the command
		self.__botHandlers.append (MessageHandler(Filters.command, self.__unknownCommand))

		for handler in self.__botHandlers:
			self.__botDispatcher.add_handler(handler)

		return

	# This first set of functions are used to configurate the bot and its workings
	# those not altere the bot's behavior in any way

	# Function to make the bot start polling for messages
	def startPolling(self):
		if(self.__isPolling):
			return False

		self.__isPolling = True
		self.__botUpdater.start_polling()
		return True

	# Function to make the bot stop polling for messages
	def stopPolling(self):
		if(not self.__isPolling):
			return False

		self.__isPolling = False
		self.__botUpdater.stop()
		return True

	# Returns if the bot is polling for messages
	def isPolling(self):
		return self.__isPolling

	# Function to add new admins
	def addAdmins(self, adminsid):
		for personid in adminsid:
			if(personid not in self.__botAdmins):
				self.__botAdmins.append (personid)

		return

	# Function to remove admins, can't remove the superadmin
	def removeAdmins(self, adminsid):
		for personid in adminsid:
			if(personid in self.__botAdmins and personid != self.__botSuperAdmin):
				self.__botAdmins.remove (personid)

		return

	# Returns the current super admin
	def getSuperAdmin(self):
		return self.__botSuperAdmin

	# Return a list of all the admins
	def getAdmins(self):
		return self.__botAdmins

	# Returns the current state of the bot
	def getCurrentState(self):
		return self.__currentState

	# This set of functions will be the callback options that will define the bot's behavior

	def __unknownCommand(self, bot, update):
		chatId = update.message.chat_id
		returningMessage = "Sorry, I don't understand your request"
		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __addAdmin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId != self.__superAdmin):
			returningMessage = "Only the real boss can add new admins!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		for personid in args:
			if(personid not in self.__botAdmins):
				self.__botAdmins.append (personid)

		return

	def __removeAdmin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId != self.__superAdmin):
			returningMessage = "Only the real boss can add new admins!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		for personid in args:
			if(personid in self.__botAdmins and personid != self.__botSuperAdmin):
				self.__botAdmins.remove (personid)

		return

	def __listAdmins(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		returningMessage = ""

		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		for personid in self.__botAdmins:
				returningMessage += personid + "\n"

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __getUserId(self, bot, update):
		chatId = update.message.chat_id
		returningMessage = "Your id is: " + str(update.message.from_user.id)
		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __resumeBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		if (self.__currentState != BotState.SLEEPING):
			returningMessage = "I'm not sleeping!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return
		
		returningMessage = "Let's start working again!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.ACTIVATED

		return

	def __startBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		if (self.__currentState != BotState.DEACTIVATED):
			returningMessage = "I'm already working!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return
		
		returningMessage = "Let's start working!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.ACTIVATED

		return

	def __stopBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		returningMessage = "Good bye!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.DEACTIVATED

		return

	def __sleepBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		if (self.__currentState != BotState.ACTIVATED):
			returningMessage = "I'm not working right now!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		returningMessage = "Good bye!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.SLEEPING

		return

	def __getCurrentState(self, bot, update):
		chatId = update.message.chat_id

		if(self.__currentState == BotState.ACTIVATED):
			returningMessage = "I'm working"

		if(self.__currentState == BotState.DEACTIVATED):
			returningMessage = "I'm not working"

		if(self.__currentState == BotState.SLEEPING):
			returningMessage = "I'm sleeping"

		bot.send_message(chat_id=chatId, text=returningMessage)

		return