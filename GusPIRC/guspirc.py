docs = """
__________
|GusPIRC |
|\_\_\_\_|
|________|

The simple, event-driven (separate thread main loop), low-level IRC lirary everyone wants.

To connect to IRC, all you have to do is to do a IRCConnector object and use the function
addSocketConnection() to add a connection to the server!

Then, parse all the messages received by receiveAllMessages() or just the latest one which
is returned by receiveLatestMessage()!
"""

disclaimer = """

Warning: Connecting to the same server and port multiple times may result in failure! This
module is no warranty that your bot will work. Much will depend in the modules that use
this interface!

Remember, this is a IRC INTERFACE, not a IRC BOT!

"""

# GusPIRC
#
# The simple, event-driven (main loop), low-level IRC library everyone wants

from iterqueue import IterableQueue
import socket
from time import sleep
from threading import Thread

class IRCConnector(object):
    """The main connector with the IRC world!

    It must only be used once!

    And it's __init__ won't connect to a server by itself. Use
    addConnectionSocket() function for this!"""

    def __init__(self):
        """Are you really willing to call this?"""
        self.connections = []

        t = Thread(target=self.mainloop)

        t.start()

    def addConnectionSocket(self, server, port = 6667, ident = "GusPIRC", realname = "A GusPIRC Bot", nickname = "GusPIRC Bot", password = "",
    email = "email@address.com", account_name = "", has_account = False, channels = None, authnumeric = 001):
        """Adds a IRC connection.

        Only call this ONCE PER SERVER! For multiple channels give a
        tuple with all the channel names as string for the argument channels!

        This function only works for NICKSERV-CONTAINING SERVERS!

        - server is the server address to connect to.
        Example: irc.freenode.com

        - port is the port of the server address.
        Example and default value: 6667

        - ident is the ident the bot's hostname will use! It's usually limited
        to 10 characters.

        Example: ident_here
        Result: botnick!~ident_here@ip_here
        Default value: "GusPIRC"

        - realname is the bot's real name displayed in most IRC clients.

        Example: GusBot(tm) the property of Gustavo6046

        - nickname is the nick of the bot (self-explanatory)

        Example: YourBotsName

        - password is the password of the bot.

        Example: password123bot

        USE WITH CAUTION! Don't share the password to anyone! Only to extremely
        trustable personnel! Only load it from a external file (like password.txt)
        and DON'T SHARE THE PASSWORD, IN SOURCE CODE, OR IN FILE!!!

        - email is the email the server should send the registration email to
        if has_account is set to False (see below!)

        Example and default value: email@address.com

        - account_name is the name of the NickServ account the bot will
        use.

        Default value: ""

        Example: botaccount
        Default value: ""

        - has_account: is a bool that determines if the bot already has a registered
        account.

        - channels: iterable object containing strings for the names of all the
        channels the bot should connect to upon joining the network.

        Example: (\"#botters-test\", \"#python\")
        Default value: None (is later defaulted to (\"#<insert bot's nickname here>help\"))

        - authnumeric: the numeric after which the bot can auth.

        Defaults to 001, but it's a highly unrecommended numeric because it may result in
        the both authing as soon as it succesfully connects to the network."""

        if not hasattr(channels, "__iter__"):
            raise TypeError("channels is not iterable!")

        print "Iteration check done!"

        # | The following commented-out code is known to be faulty and thus
        # | was commented out.

        # if socketindexbyaddress(server, port) != -1:
        #     print "Warning: Trying to append socket of existing address!"
        #     return False
        #
        # print "Check for duplicates done!"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print "Socket making done!"

        sock.connect((server, port))

        print "Connected socket!"

        sock.sendall("USER %s * * :%s\r\n" % (ident, realname))
        if not has_account:
            sock.sendall("NICK %s\r\n" % (account_name))
        else:
            sock.sendall("NICK %s\r\n" % (nickname))

        print "Sent first commands to socket!"

        # function used for breaking through all loops
        def waituntilnotice():
            """This function is NOT to be called!
            It's a solution to the \"break only innerest loop\" problem!"""
            buffering = ""
            while True:
                x = sock.recv(4096)

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
                    except IndexError:
                        continue
                    if compdata == str(authnumeric):
                        return

        waituntilnotice()

        print "NickServ Notice found!"

        if not has_account:
            sock.sendall("PRIVMSG ChanServ :REGISTER %s %s\r\n" % (password, email))
            print "Made account!"

        sock.sendall("PRIVMSG ChanServ :IDENTIFY %s %s\r\n" % (account_name, password))

        print "Authenticated!"

        if channels == None:
            channels = ("#%shelp" % (nickname))
            print "Channel defaulting done!"
        else:
            print "Channel defaulting check done!"

        for x in channels:
            sock.sendall("JOIN %s\r\n" % (x))

        print "Joined channels!"

        self.connections.append([sock, IterableQueue(), IterableQueue()])

        print "Added to connections!"

        return True

    def mainloop(self):
        """Again not to be called!

        It's the main loop mentioned in the docs.

        It's called in a different thread, and by __init__() so don't even
        WORRY with this!"""
        while True:
            for x in self.connections:

                buffering = ""
                while True:
                    w = x[0].recv(4096)

                    if not w.endswith("\r\n"):
                        buffering += w
                        continue

                    if buffering != "":
                        w = "%s%s" % (buffering, w)
                        buffering = ""

                    if len(w.split("\r\n")) > 2:
                        y = w.split("\r\n")
                        y.pop(-1)
                    else:
                        y = (w.strip("\r\n"))

                    break

                for z in y:
                    x[1].put(z.strip("\r\n"))
                    if z.split(" ")[0] == "PING":
                        x[0].sendall("PONG :%s\r\n" % (z.split(":")[1]))
                    print z
                    try:
                        if z.split(" ")[0].strip(":") == "QUIT" or z.split(" ")[1] == "QUIT":
                            self.connections[self.connections.index(x)][0].close()
                            self.connections.remove(x)
                    except IndexError:
                        pass

                for x in self.connections:
                    msg = x[2].get()
                    print msg
                    x[0].sendall(msg)

                sleep(3.00/4.00)

    def sendcommand(self, connectionindex = 0, command = ""):
        """Sends a command to the IRC server.

        - connectionindex: the index of the connection. Usually in the order
        you called addConnectionSocket().

        - command: the command string, including \":\" and \"PRIVMSG\" instead
        of \"MSG\" or \"SAY\". Don't include \"\\r\\n\", it's automatically added!"""
        connections[connectionindex][2].put("%s\r\n"% (command))

    def sendmessage(self, connectionindex = 0, target = "ChanServ", message = "Error: No message argument provided to bot!"):
        """Sends a message to the target in the IRC server.

        - connectionindex: the index of the connection. Usually in the order
        you called addConnectionSocket().

        - target: the target. Usually a channel name (like #python) (replaces SAY)
        or a nickname (replaces MSG).

        Defaults to sending ChanServ commands for a good reason!

        - message: the message sent to the target. Self-explanatory, I hope."""
        connections[connectionindex][2].put("PRIVMSG %s :%s\r\n" % (target, message))

    def disconnect(self, connectionindex = 0, message = "a GusPirc bot: The simplest Python low-level IRC interface"):
        """Disconnects from the server in the index specified.

        - connectionindex: the index of the connection. Usually in the order
        you called addConnectionSocket().

        - message: the quit message. Self-explanatory."""
        connections[connectionindex][2].put("QUIT :%s\r\n") % (message)

    def receivelatestmessage(self, index = 0):
        """Returns the last message from the queue of received messages from
        the IRC socket.

        - index: the index of the connection. Ususally in the order you called
        addConnectionSocket()."""
        return self.connections[index][1].get()

    def socketindexbyaddress(self, address, port = 6667):
        """Returns the index of the IRC connection that is connected t
        address:port or -1 if there aren't any."""
        if self.connections != []:
            for x in self.connections:
                if tuple(x.getsockname()[:2]) == (address, port):
                    return self.connections.index(x)
        return -1

    def receiveallmessages(self, index = 0):
        """Returns all the messages from the queue in the
        connection.

        - index: the index of the connection. Usually in the order you called
        addConnectionSocket()."""
        return [i for i in self.connections[index][1]]
