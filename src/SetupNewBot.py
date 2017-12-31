#This file right now is only for testing purposes

from chatBot.ChatBot import ChatBot
bot1 = ChatBot(token='485439619:AAGq3c3JpwYqWacrJjx1Z8nsju1wWEq63iU',superadminid='479199261',adminsid=['479199261'], debuglevel=2)
bot1.startPolling()


from cryptoExchanger.BittrexExchanger import BittrexExchanger
exc1 = BittrexExchanger(key='f1a56fde65ef46ee9891abb2ee54c57c',secret='65d517352208484699a015c362ef3603')
exc1.getListMarkets()


from CryptoBot import CryptoBot
bot1 = CryptoBot(token='485439619:AAGq3c3JpwYqWacrJjx1Z8nsju1wWEq63iU',superadminid='479199261', debuglevel=2)
bot1.startPolling()