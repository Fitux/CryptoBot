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
from telegram.ext import MessageHandler, Filters, Handler
from telegram.ext.dispatcher import DispatcherHandlerStop
from enum import Enum
from collections import defaultdict

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
	__botAdmins = []
	__botSuperAdmin = None
	__deactivatedHandler = None
	
	_unknownHandler = None
	_debugLevel = None

	def __init__(self, token, superadminid, adminsid=[], debuglevel=0):
		# Defining the basic variables needed to work
		# The __currentState will be based on the BotState Enum implementation
		# The __accessToken is the identifier needed for the bot to connect
		# The __botSuperAdmin is the administrator that shouldn't be removed by any circunstances
		# The __botAdmins are the other administrators that can execute the bot commands

		self._debugLevel = debuglevel

		if (self._debugLevel > 0): print "Debug Level: " + str(debuglevel) + "\n"

		self.__currentState = BotState.DEACTIVATED
		if (self._debugLevel >= 1): print "Bot Deactivated\n"
		self.__accessToken = token
		if (self._debugLevel >= 1): print "Token: " + token + "\n"
		self.__botSuperAdmin = superadminid
		if (self._debugLevel >= 1): print "SuperAdmin: " + superadminid + "\n"
		self.__botAdmins.append (superadminid)


		for personid in adminsid:
			if(personid not in self.__botAdmins):
				if (self._debugLevel >= 1): print "Admin: " + personid
				self.__botAdmins.append (personid)

		# The __isPolling is a flag that will let us know if the bot is polling for messages
		# The __botUpdater is the one in charge of update the chatbot and contains the dispatcher
		# The __botDispatcher is the one in charge of call the correct handlers used by the messages
		self.__isPolling = False
		self.__botUpdater = Updater(token=self.__accessToken)
		self.__botDispatcher = self.__botUpdater.dispatcher

		self.__deactivatedHandler = MessageHandler(Filters.command, self.__deactivatedCommand)
		self._unknownHandler = MessageHandler(Filters.command, self.__unknownCommand)

		if (self._debugLevel >= 1): print "Adding Priority Handlers\n"
		# Here we will add all the priority handlers needed for the chat bot
		self._addCommandHandler('startBot', self.__startBot, group=0)
		self._addCommandHandler('stopBot', self.__stopBot, group=0)
		self._addCommandHandler('resumeBot', self.__resumeBot, group=0)
		self._addCommandHandler('sleepBot', self.__sleepBot, group=0)
		self._addCommandHandler('botState', self.__getCurrentState, group=0)

		self._addHandler(self.__deactivatedHandler, group=0)

		if (self._debugLevel >= 1): print "Adding Other Handlers\n"
		# Here we will add all the basic handlers needed for the chat bot
		self._addCommandHandler('listAdmins', self.__listAdmins)
		self._addCommandHandler('removeAdmin', self.__removeAdmin, pass_args=True)
		self._addCommandHandler('addAdmin', self.__addAdmin, pass_args=True)
		self._addCommandHandler('myUserId', self.__getUserId)

		self._addHandler(self._unknownHandler)

		return

	# This first set of functions are used to configurate the bot and its workings
	# those not altere the bot's behavior in any way

	# Function to add new handlers to the bot, it should be only used during the init of the class
	def _addCommandHandler(self, command, callback, pass_args=False, group=1):
		if (self._debugLevel >= 2): print "Adding Command Handler: " + command
		self.__botDispatcher.add_handler(CommandHandler(command, callback, pass_args=pass_args), group=group)
		return

	def _addMessageHandler(self, filters, callback, group=1):
		if (self._debugLevel >= 2): print "Adding Message Handler"
		self.__botDispatcher.add_handler(MessageHandler(filters, callback), group=group)
		return

	def _addHandler(self, handler, group=1):
		if (self._debugLevel >= 2): print "Adding Handler"
		self.__botDispatcher.add_handler(handler, group=group)
		return

	def _removeHandler(self, handler, group=1):
		if (self._debugLevel >= 2): print "Removing Handler"
		self.__botDispatcher.remove_handler(handler, group=group)
		return

	# Function to make the bot start polling for messages
	def startPolling(self):
		if(self.__isPolling):
			return False

		if (self._debugLevel >= 1): print "Started Polling\n"
		self.__isPolling = True
		self.__botUpdater.start_polling()
		return True

	# Function to make the bot stop polling for messages
	def stopPolling(self):
		if(not self.__isPolling):
			return False

		if (self._debugLevel >= 1): print "Stopped Polling\n"
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
				if (self._debugLevel >= 1): print "Adding Admin: " + personid + "\n"
				self.__botAdmins.append (personid)

		return

	# Function to remove admins, can't remove the superadmin
	def removeAdmins(self, adminsid):
		for personid in adminsid:
			if(personid in self.__botAdmins and personid != self.__botSuperAdmin):
				if (self._debugLevel >= 1): print "Removing Admin: " + personid + "\n"
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
	def __deactivatedCommand(self, bot, update):
		chatId = update.message.chat_id
		returningMessage = "Sorry, I'm not working right now"

		if (self._debugLevel >= 1): print "Deactivated command"

		bot.send_message(chat_id=chatId, text=returningMessage)

		raise DispatcherHandlerStop
		return

	def __unknownCommand(self, bot, update):
		chatId = update.message.chat_id
		returningMessage = "Sorry, I don't understand your request"

		if (self._debugLevel >= 1): print "Unknown command"

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __addAdmin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (self._debugLevel >= 1): print "Add admin command"

		if (userId != self.__superAdmin):
			returningMessage = "Only the real boss can add new admins!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		self.addAdmins(args)

		return

	def __removeAdmin(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)

		if (self._debugLevel >= 1): print "Remove Admin command"
		
		if (userId != self.__superAdmin):
			returningMessage = "Only the real boss can add new admins!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		self.removeAdmins(args)

		return

	def __listAdmins(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		returningMessage = ""

		if (self._debugLevel >= 1): print "List Admins command"

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

		if (self._debugLevel >= 1): print "User ID command"

		bot.send_message(chat_id=chatId, text=returningMessage)

		return

	def __resumeBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)

		if (self._debugLevel >= 1): print "Resume Command"

		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		if (self.__currentState != BotState.SLEEPING):
			returningMessage = "I'm not sleeping!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return
		
		if (self._debugLevel >= 1): print "Resuming..."

		returningMessage = "Let's start working again!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.ACTIVATED

		self.__botDispatcher.remove_handler(self.__deactivatedHandler, group=0)
		raise DispatcherHandlerStop
		return

	def __startBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)

		if (self._debugLevel >= 1): print "Start command"
		
		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		if (self.__currentState != BotState.DEACTIVATED):
			returningMessage = "I'm already working!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return
		
		if (self._debugLevel >= 1): print "Starting..."

		returningMessage = "Let's start working!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.ACTIVATED

		self.__botDispatcher.remove_handler(self.__deactivatedHandler, group=0)
		raise DispatcherHandlerStop
		return

	def __stopBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)

		if (self._debugLevel >= 1): print "Stop command"

		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		if (self._debugLevel >= 1): print "Stopping..."
		returningMessage = "Good bye!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.DEACTIVATED

		self.__botDispatcher.remove_handler(self.__deactivatedHandler, group=0)
		self.__botDispatcher.add_handler(self.__deactivatedHandler, group=0)

		raise DispatcherHandlerStop
		return

	def __sleepBot(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (self._debugLevel >= 1): print "Sleep command"

		if (userId not in self.__botAdmins):
			returningMessage = "You are not my boss!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		if (self.__currentState != BotState.ACTIVATED):
			returningMessage = "I'm not working right now!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		if (self._debugLevel >= 1): print "Sleeping..."

		returningMessage = "Good bye!"
		bot.send_message(chat_id=chatId, text=returningMessage)
		self.__currentState = BotState.SLEEPING

		self.__botDispatcher.remove_handler(self.__deactivatedHandler, group=0)
		self.__botDispatcher.add_handler(self.__deactivatedHandler, group=0)

		raise DispatcherHandlerStop
		return

	def __getCurrentState(self, bot, update):
		chatId = update.message.chat_id

		if (self._debugLevel >= 1): print "Get State command\n"

		if(self.__currentState == BotState.ACTIVATED):
			returningMessage = "I'm working"

		if(self.__currentState == BotState.DEACTIVATED):
			returningMessage = "I'm not working"

		if(self.__currentState == BotState.SLEEPING):
			returningMessage = "I'm sleeping"

		bot.send_message(chat_id=chatId, text=returningMessage)

		raise DispatcherHandlerStop
		return 