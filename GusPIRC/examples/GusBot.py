#-----------------------------------------------------------------------------------#
# Name: . . . . . . Talking to Learn(TM) . . . . . . . . . . . . . . . . . . . . . .#
# Purpose:. . . . . Just a normal markov list. . . . . . . . . . . . . . . . . . . .#
# . . . . . . . . . Originally a innovative system, but it was scrapped. . . . . . .#
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . #
# Author: . . . . . Gustavo Ramos "Gustavo6046" Rehermann. . . . . . . . . . . . . .#
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . #
# Created:. . . . . 17/03/2016 . . . . . . . . . . . . . . . . . . . . . . . . . . .#
# Copyright:. . . . (c) Gustavo6046 2016 . . . . . . . . . . . . . . . . . . . . . .#
# Licence:. . . . . CC BY-NC-SA 3.0 International. . . . . . . . . . . . . . . . . .#
# Base Bot Author: .mrtux and OldCoder. . . . . . . . . . . . . . . . . . . . . . . #
#-----------------------------------------------------------------------------------#

from iterqueue import IterableQueue
import os
import re
import signal
import socket
import sys
from ast import literal_eval
from time import sleep
from threading import Thread
from ujson import dumps
from ujson import loads
from markovclasses import *
from guspirc import IRCConnector

def parsemsg(ircmsg, connector, ip, index):

    if "ERROR" == msgmode or ("QUIT" == msgmode and botnick == ircmsg.msgargs(" ")[0].strip(":")):
        return False

    if not "PRIVMSG" in msgmode:
        return True

# detects message details
    try:
        msgargs = ircmsg.msgargs(":")[2].msgargs(" ")
        msgchan = ircmsg.msgargs(" ")[2]
        msgmode = ircmsg.msgargs(" ")[1]
        msgsrc  = ircmsg.msgargs(" ")[0].strip(":")
        msgnick = ircmsg.msgargs(" ")[0].msgargs("!")[0].strip(":")
    except IndexError:
        pass # ignore the message for now

    if "!say" == msgargs[0]:
        say_msgargs = ircmsg.msgargs ("!say ")
        connector.sendmessage(msgchan, say_msgargs[1])
        connector.sendmessage(master, "Message sent: " + say_msgargs[1])
        return True

# adds messages to lexical repository
    if(msgargs(" ")[3][1:2] != "!" and
    msgargs(" ")[0] != botnick + "@~" + uname + "!" + ip and
    msgargs(" ")[0] != botnick + "!~" + uname + "@unaffiliated/" + uname):
        for x in xrange(1, len(msgargs) - 1):
            if msgargs[x-1] == msgargs[x] or msgargs[x-1] == msgargs[x+1] or msgargs[x+1] == msgargs[x]:
                continue
            tree.addmarkovkeyword(msgargs[x-1], msgargs[x], msgargs[x+1])
            print "%s,%s,%s" % (msgargs[x-1], msgargs[x], msgargs[x+1])
        return True

# authenticating command
    if "!auth" == msgargs[0]:
        connector.sendmessage("NickServ", "IDENTIFY " + password)
        connector.sendmessage(msgnick, "Authed!")
        return True

# handles channel parting and joining
    if "!join" == msgargs[0]:
        if len(_msgargs) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
        try:
            connector.sendcommand("JOIN %s :%s" % (msgargs[1], " ".join(msgargs[2:])))
        except IndexError:
            connector.sendcommand("JOIN %s" % (msgargs[1]))
        return True

    if "!part" == msgargs[0]:
        if len(msgargs) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
            return True

        try:
            connector.sendcommand("PART %s :%s" % (msgargs[1], " ".join(msgargs[2:])))
        except IndexError:
            connector.sendcommand("PART %s" % (msgargs[1]))
        return True

# Help message
    if ":!commands" in ircmsg or ircmsg.find(":!help") != -1 or ircmsg.find(":!list") != -1:
        connector.sendmessage(msgchan, "Commands:")
        connector.sendmessage(msgchan, "!sayabout topic : Say stuff based on the topic")
        connector.sendmessage(msgchan, "!owner . . . . .: Tells who owns this bot")
        connector.sendmessage(msgchan, "!nick . . . . . : Changes the bot's nickname ()")
        connector.sendmessage(msgchan, "!savedefs . . . : Saves the current lexical tree in owner's HDD ()")
        connector.sendmessage(msgchan, "!wordcount . . .: How many words are there in the Markov list?")
        connector.sendmessage(msgchan, "!loaddefs . . . : Loads the lexical tree from file in owner's HDD ()")
        connector.sendmessage(msgchan, "!source . . . . : Messages the source to the command executor")
        connector.sendmessage(msgchan, "!eval . . . . . : Evaluates a expression. Algebra not supported.")
        connector.sendmessage(msgchan, "!raw . . . . . .: Executes a IRC command. ()")
        connector.sendmessage(msgchan, "!flushq . . . . : Flushes message queue")
        connector.sendmessage(msgchan, "!join and !part : Joins and parts channels respectively")
        connector.sendmessage(msgchan, " ")
        connector.sendmessage(msgchan, "() means the command is only for the bot's owner.")
        connector.sendmessage(msgchan, "For more info refer to irc.freenode.net #gusbot")
        connector.sendmessage(msgchan, "Thank you for reading and not making a mess!")
        return True

# tells who is the owner
    if "!owner" == msgargs[0]:
        connector.sendmessage (msgchan, "My owner is: %s" % (master))
        return True

# word count
    if "!wordcount" == msgargs[0]:
        connector.sendmessage (msgchan, "There are %s words." % (str(len(tree.allwords))))
        return True

# change nick
    if "!nick" == msgargs[0] and master in ircmsg.msgargs(" ")[0]:
        connector.sendcommand("NICK %s" % str_msgargs[1])
        connector.sendmessage (msgchan, "Nick changed to %s." % (str_msgargs [1]))
        return True

# quits the network
    if "!quit" == msgargs[0] and master in ircmsg.msgargs(" ")[0]:
        try:
            connector.sendcommand("QUIT :%s" % (" ".join(msgargs[1:])))
        except IndexError:
            connector.sendcommand("QUIT :A GusPIRC bot leaves the network. So sad, one less in activity!")
        return False

# say about some topic
    if "!sayabout" == msgargs[0]:
        if len(msgargs) < 2:
            connector.sendmessage(msgchan, "What topic?")
        else:
            if tree.composephrase(str_msgargs[1]) == None:
                connector.sendmessage(msgchan, "No such topic in my list, sorry!")
            else:
                connector.sendmessage (msgchan, tree.composephrase(str_msgargs[1]))
        return True

# saves current Markov chain
    if "!savedefs" == msgargs[0] and master in ircmsg.msgargs(" ")[0]:
        if len(msgargs) < 2:
            connector.sendmessage (msgchan, "Not enough arguments!")
        open(msgargs[1], "w").write(dumps(str_msgargs[0]))
        connector.sendmessage (msgchan, "Sent  to file " + str_msgargs[0] + " with success!")
        return True

# loads current Markov chain
    if "!loaddefs" == msgargs[0] and master in ircmsg.msgargs(" ")[0]:
        if len(str_msgargs) == 0:
            connector.sendmessage (msgchan, "No argument given! Aborting...")
            return True
        tree = loads(open(str_msgargs[0], "w").read)

# messages all source to messager
    if "!source" == msgargs[0]:
        mysource = open("__main__.py", "r")
        x = "\b"
        while x != "":
            x = mysource.readline()
            connector.sendmessage(msgnick, x)
            sleep(1.0/(8.0/5.0))
        mysource.close()

# evaluates expression
    if "!eval" == msgargs[0]:
        if len(args) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
            return True
        try:
            connector.sendmessage(msgchan, "Result: " + str(literal_eval(" ".join(msgargs[1:]))))
        except (ValueError, SyntaxError):
            connector.sendmessage(msgchan, "Incorrect equation string!")

# executes command
    if "!raw" == msgargs[0] and master in ircmsg.msgargs(" ")[0]:
        connector.sendcommand(ircmsg.msgargs(":!raw")[1])

# flushes the command queue
    if "!flushqueue" == msgargs[0]:
        print "Flushed %i messages and IRC commands." % (len(connector.connections[index][1]))
        savemsgs = []
        for i in connector.connections[index][1]:
            if "PONG :" in i or "NICK :" in i or "JOIN :" in i or "PART :" in i or "QUIT :" in i or "NickServ" in i or "ChanServ" in i:
                savemsgs.append(i)
        connector.connections[index][1] = IterableQueue()
        for i in savemsgs:
            connector.connections[index][1].put(i)

if __name__ == "__main__":

    print "Defining variables!"

    tree = MarkovChain()
    print "Markov chain defined!"

    connector = IRCConnector()
    print "Connector defined!"

    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    print "Connecting to servers!"

    connector.addConnectionSocket(server="irc.freenode.org", port=6667, ident="GusUtils", realname="GusBot(tm) the property of Gustavo6046", nickname="GusBot", password=open("password.txt", "r").read().strip("\n"), email="gugurehermann@gmail.com", account_name="GusBot", has_account=True, channels=("#botters-test", "#botters", "##hardware", "#grafx2"), authnumeric=376)
    connector.addConnectionSocket(server="irc.zandronum.com", port=6667, ident="GusUtils", realname="GusBot(tm) the property of Gustavo6046", nickname="GusBot", password=open("password.txt", "r").read().strip("\n"), email="gugurehermann@gmail.com", account_name="GusBot", has_account=True, channels=("#bottest", "#botspam"), authnumeric=267)

    print "Added loop for exiting!"

    while True:
        for i in xrange(len(connector.connections) - 1):
            for x in connector.receiveallmessages(i):
                if parsemsg(x, connector, ip, i) == False:
                    sys.exit(0)
