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

    if "PING" == ircmsg.split(" ")[0]:
        connector.sendcommand("PONG :%s%s" % (ircmsg.split(":")[1]))

    # detects what channel is the last message's
    try:
        msgchan = ircmsg.split(" ")[2]
        msgmode = ircmsg.split(" ")[1]
        msgsrc  = ircmsg.split(" ")[0].strip(":")
    except IndexError:
        pass # ignore the message for now

    print ircmsg

    irc_split = ircmsg.split(" ")

    if "ERROR" == msgmode or ("QUIT" == msgmode and botnick == ircmsg.split(" ")[0].strip(":")):
        return False

    if not "PRIVMSG" in msgmode:
        return True

    if ":!say" in ircmsg and not ":!sayabout" in ircmsg:
        say_split = ircmsg.split ("!say ")
        connector.sendmessage(msgchan, say_split[1])
        connector.sendmessage(master, "Message sent: " + say_split[1])

# authenticating command
    if "!auth" in ircmsg:
        cmdargs = ircmsg.split(":")[2].split(" ")
        connector.sendmessage("NickServ", "IDENTIFY " + password)
        connector.sendmessage(ircmsg.split(":")[1].split("@")[0], "Authed!")

# adds messages to lexical repository
    if(ircmsg.split(" ")[3][1:2] != "!" and
    ircmsg.split(" ")[0] != botnick + "@~" + uname + "!" + ip and
    ircmsg.split(" ")[0] != botnick + "!~" + uname + "@unaffiliated/" + uname):
        split = ircmsg.split(":")[2].split(" ")
        for x in xrange(1, len(split) - 1):
            if split[x-1] == split[x] or split[x-1] == split[x+1] or split[x+1] == split[x]:
                continue
            tree.addmarkovkeyword(split[x-1], split[x], split[x+1])
            print "%s,%s,%s" % (split[x-1], split[x], split[x+1])

# handles channel parting and joining
    if ":!join" in ircmsg != -1:
        str_split = ircmsg.split(":")[2].split(" ")
        if len(str_split) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
        try:
            connector.sendcommand("JOIN " + str_split[1] + " " + str_split[2])
        except IndexError:
            connector.sendcommand("JOIN " + str_split[1])

    if ":!part" in ircmsg:
        str_split = ircmsg.split(":")[2].split(" ")
        if len(str_split) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
            return True
        try:
            connector.sendcommand("PART " + str_split[1] + " " + str_split[2])
        except IndexError:
            connector.sendcommand("PART " + str_split[1])

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
        connector.sendmessage(msgchan, " ")
        connector.sendmessage(msgchan, "() means the command is only for the bot's owner.")
        connector.sendmessage(msgchan, "For more info refer to irc.freenode.net #gusbot")
        connector.sendmessage(msgchan, "Thank you for reading and not making a mess!")

# tells who is the owner
    if ":!owner" in ircmsg:
        connector.sendmessage (msgchan, "My owner is: %s%s" % (master))

# word count
    if ":!wordcount" in ircmsg:
        connector.sendmessage (msgchan, "There are %s words.%s" % (str(len(tree.allwords))))

# change nick
    if ":!nick" in ircmsg and master in ircmsg.split(" ")[0]:
        str_split = ircmsg.split("!nick ")
        connector.sendcommand("NICK " + str_split[1])
        connector.sendmessage (msgchan, "Nick changed to " + str_split [1] + ".")

# quits the network
    if ":!quit" in ircmsg and master in ircmsg.split(" ")[0]:
        connector.sendcommand("QUIT")
        return

# say about some topic
    if ":!sayabout" in ircmsg:
        str_split = ircmsg.split(":")[2].split(" ")
        if len(str_split) < 2:
            connector.sendmessage(msgchan, "What topic?")
        else:
            if tree.composephrase(str_split[1]) == None:
                connector.sendmessage(msgchan, "No such topic in my list, sorry!")
            else:
                connector.sendmessage (msgchan, tree.composephrase(str_split[1]))

# saves current Markov chain
    if ":!savedefs" in ircmsg and master in ircmsg.split(" ")[0]:
        str_split = ircmsg.split("!savedefs ")[1].split(" ")
        if len(str_split) == 0:
            connector.sendmessage (msgchan, "No argument given! Aborting...")
            return True
        open(str_split[1], "w").write(dumps(str_split[0]))
        connector.sendmessage (msgchan, "Sent  to file " + str_split[0] + " with success!")

# loads current Markov chain
    if ":!loaddefs" in ircmsg and master in ircmsg.split(" ")[0]:
        str_split = ircmsg.split("!loaddefs ")[1].split(" ")
        if len(str_split) == 0:
            connector.sendmessage (msgchan, "No argument given! Aborting...")
            return True
        tree = loads(open(str_split[0], "w").read)

# messages all source to messager
    if ":!source" in ircmsg:
        othernick = ircmsg.split("!")[0][1:]
        mysource = open("__main__.py", "r")
        x = "\b"
        while x != "":
            x = mysource.readline()
            connector.sendmessage(othernick, x)
            sleep(1.0/(8.0/5.0))
        mysource.close()

# evaluates expression
    if ":!eval" in ircmsg:
        args = ircmsg.split(":")[2].split(" ")
        args.pop(0)
        if len(args) < 2:
            connector.sendmessage(msgchan, "Invalid number of arguments!")
            return True
        try:
            connector.sendmessage(msgchan, "Result: " + str(literal_eval(" ".join(args))))
        except (ValueError, SyntaxError):
            connector.sendmessage(msgchan, "Incorrect equation string!")

# executes command
    if ":!raw" in ircmsg and master in ircmsg.split(" ")[0]:
        connector.sendcommand(ircmsg.split(":!raw")[1])

# flushes the command queue
    if ":!flushqueue" in ircmsg:
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

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect("google.com", 0)
    ip = ip.getsockname()[0]
    print "Host IP determined!"
    s.close()

    print "Connecting to servers!"

    connector.addConnectionSocket(server="irc.freenode.org", port=6667, ident="GusUtils", realname="GusBot(tm) the property of Gustavo6046", nickname="GusBot", password=open("password.txt", "r").read().strip("\n"), email="gugurehermann@gmail.com", account_name="GusBot", has_account=True, channels=("#botters-test", "#botters", "##hardware", "#grafx2"))
    connector.addConnectionSocket(server="irc.zandronum.com", port=6667, ident="GusUtils", realname="GusBot(tm) the property of Gustavo6046", nickname="GusBot", password=open("password.txt", "r").read().strip("\n"), email="gugurehermann@gmail.com", account_name="GusBot", has_account=True, channels=("#bottest", "#botspam"))

    print "Added loop for exiting!"

    while True:
        for i in xrange(len(connector.connections) - 1):
            for x in connector.receiveAllMessages(i):
                if parsemsg(x, connector, ip, i) == False:
                    sys.exit(0)
