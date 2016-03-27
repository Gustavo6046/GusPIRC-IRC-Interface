# -----------------------------------------------------------------------------------#
# Name: . . . . . . GusBot(tm) . . . . . . . . . . . . . . . . . . . . . . . . . . .#
# Name: . . . . . . GusBot(tm) . . . . . . . . . . . . . . . . . . . . . . . . . . .#
# Purpose: . . . . .Multi-use IRC bot for many tasks! Including Google and Wiki! . .#
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . #
# Author: . . . . . Gustavo Ramos "Gustavo6046" Rehermann. . . . . . . . . . . . . .#
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . #
# Created:. . . . . 17/03/2016 . . . . . . . . . . . . . . . . . . . . . . . . . . .#
# Copyright:. . . . (c) Gustavo6046 2016 . . . . . . . . . . . . . . . . . . . . . .#
# Licence:. . . . . CC BY-NC-SA 3.0 International. . . . . . . . . . . . . . . . . .#
# -----------------------------------------------------------------------------------#

from sys import exit, path
from threading import Thread
from json import dump, loads
from guspirc import IRCConnector, log, clearlog

def savestuff(perms, accounts, file_):
    file_ = open(file_, "w")
    dump(perms, open("file_1.tmp", "w")), dump(accounts, open("file_2.tmp", "w"))
    file_.write("{0}|{1}".format(open("file_1.tmp").read(), open("file_2.tmp").read()))
    file_.close()


def loadstuff(json):
    print repr(json)
    return loads(json.split("|")[0]), loads(json.split("|")[1])

if __name__ == "__main__":

    clearlog()

    path.insert(0, ".\plugins")
    log(u"Added plugins folder to path!")

    tree = {}
    log(u"Markov chain defined!")

    plugins = []
    log(u"Plugins defined!")

    connector = IRCConnector()
    log(u"Connector defined!")

    threads = []
    wiki = []

    connector.addconnectionsocket(
        server="irc.freenode.org",
        ident="GusUtils",
        realname="GusBot(tm) the property of Gustavo6046",
        nickname="GusBot",
        password=open("password.txt", "r").read().strip("\n"),
        email="gugurehermann@gmail.com",
        account_name="GusBot",
        has_account=True,
        channels=("#botters-test", "#gusbot"),
        authnumeric=376)
    connector.addconnectionsocket(
        server="irc.zandronum.com",
        ident="GusUtils",
        realname="GusBot(tm) the property of Gustavo6046",
        nickname="GusBot",
        password=open("password.txt", "r").read().strip("\n"),
        email="gugurehermann@gmail.com",
        account_name="GusBot",
        has_account=True,
        channels=("#bottest", "#botspam"),
        authnumeric=267)

    log(u"Connected to servers! Main Server IO loop started")


    def ioloop(i, connect, tre, plugi, wik):

        import msgparser

        perms = msgparser.Permlevels()
        accounts = {}
        loggedusers = msgparser.LoggedUsers()

        while True:

            msgs = []

            connect.mainloop(i)

            for x in connect.receiveallmessages(i):

                try:
                    z = loadstuff(open("server{0:s}.ui".format(connector.connections[i][6]), "r").read())
                    perms = z[0]
                    accounts = z[1]
                except IOError:
                    pass
                except ValueError:
                    log(u"Warning: Invalid JSON file! Retrying with empty user info...")

                print x

                try:
                    if x.split(":")[2].split(" ")[0] == "!reloadparser":
                        reload(msgparser)
                        connect.sendmessage(i, x.split(" ")[2], "%s: Reloaded with success!" % (x.split("!")[0].strip(":")))
                except IndexError:
                    pass

                b = msgparser.parsemsg(x, connect, i, tre, plugi, wik, perms, accounts, loggedusers)

                if b is False:
                    exit(0)

                else:
                    if b is not None:
                        tre, plugi, wik, perms, accounts, loggedusers = b
                        try:
                            savestuff(perms, accounts, open(u"server{0:s}".format(connector.connections[i][6]), "w"))
                        except TypeError:
                            pass

                msgs.append(x)

            connect.relayoutqueue(i, msgs)


    for i in xrange(len(connector.connections)):
        threads.append(Thread(target=ioloop,
                              name="Server {0:s} Thread".format(str(connector.connections[i][0].getsockname()), ),
                              args=(i, connector, tree, plugins, wiki)))

    for i in threads:
        i.start()