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
	# The __listCommands is the list where we can know all the commands the bot has
	# The __deactivatedHandler will be the one in charge of not letting people use the bot when it is not running
	# The _unknownHandler will be the one in charge of answering when the received command does not match any of the available commands
	# The _debuglevel is the flag used to enable the printing messages for debugging

	__isPolling = None
	__currentState = None
	__accessToken = None
	__botUpdater = None
	__botDispatcher = None
	__botSuperAdmin = None

	__listCommands = {}
	__botAdmins = []
	__botBanned = []
	
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

		self.__bannedHandler = MessageHandler(Filters.command, self.__bannedCommand)
		self.__deactivatedHandler = MessageHandler(Filters.command, self.__deactivatedCommand)
		self._unknownHandler = MessageHandler(Filters.command, self.__unknownCommand)

		if (self._debugLevel >= 1): print "Adding Priority Handlers\n"
		# Here we will add all the priority handlers needed for the chat bot
		self._addCommandHandler('startBot', self.__startBot, group=0)
		self._addCommandHandler('stopBot', self.__stopBot, group=0)
		self._addCommandHandler('resumeBot', self.__resumeBot, group=0)
		self._addCommandHandler('sleepBot', self.__sleepBot, group=0)
		self._addCommandHandler('botState', self.__getCurrentState, group=0)
		self._addCommandHandler('listCommands', self.__getlistCommands, group=0)
		self._addCommandHandler('listAdmins', self.__listAdmins, group=0)
		self._addCommandHandler('removeAdmin', self.__removeAdmin, pass_args=True, group=0)
		self._addCommandHandler('addAdmin', self.__addAdmin, pass_args=True, group=0)
		self._addCommandHandler('myUserId', self.__getUserId, group=0)
		self._addCommandHandler('banUser', self.__banUser, group=0)
		self._addCommandHandler('unbanUser', self.__unbanUser, group=0)

		self._addCommandHandler('help', self.__getlistCommands, group=1)
		self._addHandler(self.__bannedHandler, group=-1)
		self._addHandler(self.__deactivatedHandler, group=0)
		self._addHandler(self._unknownHandler)

		return

	# This first set of functions are used to configurate the bot and its workings
	# those not altere the bot's behavior in any way

	# Function to add new handlers to the bot, it should be only used during the init of the class
	def _addCommandHandler(self, command, callback, pass_args=False, group=1):
		if (self._debugLevel >= 2): print "Adding Command Handler: " + command
		self.__botDispatcher.add_handler(CommandHandler(command, callback, pass_args=pass_args), group=group)
		self.__listCommands[command] = group
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

	# Returns the list of available commands
	def getListCommands(self):
		return self.__listCommands

	def unbanUsers(self, usersid):
		for personid in usersid:
			if(personid in self.__botBanned):
				if (self._debugLevel >= 1): print "Unbanning User: " + personid + "\n"
				self.__botAdmins.remove (personid)

		return

	def banUsers(self, usersid):
		for personid in usersid:
			if(personid not in self.__botBanned and personid not in self.__botAdmins):
				if (self._debugLevel >= 1): print "Banning User: " + personid + "\n"
				self.__botAdmins.append (personid)

		return

	def getBannedUsers(self):
		return self.__botBanned

	# This set of functions will be the callback options that will define the bot's behavior
	def __getlistCommands(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		returningMessage = "Here is the list of commands\n"

		if (self._debugLevel >= 1): print "Help command"

		for command in self.__listCommands:
			if(self.__listCommands[command] or userId in self.__botAdmins):
				returningMessage += "/" + command + "\n"

		bot.send_message(chat_id=chatId, text=returningMessage)

		raise DispatcherHandlerStop
		return

	def __bannedCommand(self, bot, update):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		returningMessage = "You can't use this bot since you are banned"

		if (userId in self.__botBanned):
			if (self._debugLevel >= 1): print "Banned command"
			bot.send_message(chat_id=chatId, text=returningMessage)
			raise DispatcherHandlerStop
			return

		return

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

	def __banUser(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (self._debugLevel >= 1): print "Ban user command"

		if (userId not in self.__botAdmins):
			returningMessage = "Only admins ban users!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		self.banUsers(args)

		return

	def __unbanUser(self, bot, update, args):
		chatId = update.message.chat_id
		userId = str(update.message.from_user.id)
		
		if (self._debugLevel >= 1): print "Unban user command"

		if (userId not in self.__botAdmins):
			returningMessage = "Only admins unban users!"
			bot.send_message(chat_id=chatId, text=returningMessage)
			return

		self.unbanUsers(args)

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