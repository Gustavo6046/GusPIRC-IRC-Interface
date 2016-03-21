# GusPIRC
#
# The simple, event-driven (main loop), low-level IRC library everyone wants

from iterqueue import IterableQueue
import socket
from time import sleep
from threading import Thread

class IRCConnector(object):

    def __init__(self):
        self.connections = []

        t = Thread(target=self.mainloop)

        t.start()

    def addConnectionSocket(self, server, port = 6667, ident = "MadeInGusPIRC", realname = "A GusPIRC Bot", nickname = "GusPIRC Bot", password = "", email = "email@address.com", account_name = "", has_account = False, channels = ("")):
        if not hasattr(channels, "__iter__"):
            raise TypeError("channels is not iterable!")

        print "Iteration check done!"

        if channels == (''):
            channels = ("#%shelp" % (nickname))

        print "Channel defaulting done!"

        if socketindexbyaddress(server, port) != -1:
            print "Warning: Trying to append socket of existing address!"
            return False

        print "Check for duplicates done!"

        socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM), IterableQueue()]

        socket[0].connect((server, port))

        print "Connected socket!"

        socket.sendall("USER %s * * :%s\r\n" % (ident, realname))
        if not has_account:
            socket.sendall("NICK %s\r\n" % (account_name))
        else:
            socket.sendall("NICK %s\r\n" % (nickname))

        print "Sent first commands to socket!"

        # function used for breaking through all loops
        def waituntilnotice(self):
            buffering = ""
            while True:
                x = socket.recv(4096)

                print x

                if not x.endswith("\r\n"):
                    buffering += x
                    continue

                if buffering != "":
                    x = "%s%s" % (buffering, x)
                    buffering = ""

                if len(x.split("\r\n")) > 2:
                    y = x.split("\r\n")
                    y.pop(-1)
                else:
                    y = (x)

                for z in y:
                    try:
                        compdata  = z.split(" ")[1]
                        compdata2 = z.split(" ")[0].split("@")[0].strip(":")
                    except IndexError:
                        continue
                    if compdata == "NOTICE" and compdata2 == "NickServ":
                        return

        waituntilnotice()

        print "NickServ Notice found!"

        if not has_account:
            socket.sendall("PRIVMSG ChanServ :REGISTER %s %s\r\n" % (password, email))
            print "Made account!"

        socket.sendall("NICK %s\r\n" % (nickname))
        socket.sendall("PRIVMSG ChanServ :IDENTIFY %s %s\r\n" % (account_name, password))

        print "Authenticated!"

        for x in channels:
            socket.sendall("JOIN %s\r\n" % (x))

        print "Joined channels!"

        connections.append([socket, IterableQueue(), IterableQueue()])

        print "Added to connections!"

        return True

    def mainloop(self):
        while True:
            for x in self.connections:

                while True:
                    w = socket.recv(4096)

                    print w

                    if not w.endswith("\r\n"):
                        buffering += w
                        continue

                    if buffering != "":
                        w = "%s%s" % (buffering, w)
                        buffering = ""

                    if len(w.split("\r\n")) > 2:
                        y = tuple(w.split("\r\n"))
                        y.pop(-1)
                    else:
                        y = (w)

                    break

                for z in y:
                    x[1].put(z.strip("\r\n"))
                    if z.split(" ")[0] == "PING":
                        x[0].sendall("PONG :%s\r\n" % (z.split(":")[1]))
                    print z

                for x in self.connections:
                    msg = x[2].get()
                    x[0].sendall(msg)
                    if msg.split(" ")[0] == "QUIT":
                        self.connections[self.connections.index(x)][0].close()
                        self.connections.remove(x)

    def sendcommand(self, connectionindex = 0, command = ""):
        connections[connectionindex][2].put("%s\r\n"% (command))

    def sendmessage(self, connectionindex = 0, target = "ChanServ", message = "Error: No message argument provided to bot!"):
        connections[connectionindex][2].put("PRIVMSG %s :%s\r\n" % (target, message))

    def disconnect(self, connectionindex = 0, message = "a GusPirc bot: The simplest Python low-level IRC interface"):
        connections[connectionindex][2].put("QUIT :%s\r\n") % (message)

    def receivelatestmessage(self, index = 0):
        return self.connections[index][1].get()

    def socketindexbyaddress(address, port = 6667):
        if self.connections != []:
            for x in self.connections:
                if tuple(x.getsockname()[:2]) == (address, port):
                    return self.connections.index(x)
        return -1

    def receiveallmessages(index = 0):
        return self.connections[index][1]
