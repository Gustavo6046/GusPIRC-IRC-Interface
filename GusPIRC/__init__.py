from Queue import Empty
from socket import SOCK_STREAM, socket, AF_INET, error
from threading import Thread
from time import sleep, strftime

from iterqueue import IterableQueue

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


def clearlog():
    logfile = open("..\log.txt", "w")
    logfile.write("\n")
    logfile.close()


def log(msg):
    msg = msg.encode("utf-8")
    logfile = open("..\log.txt", "a")
    x = u"[{0}]: {1}".format(strftime("%A %d - %X : GMT %Z").encode('utf-8'), msg)
    logfile.write(x)
    print x
    logfile.close()


class IRCConnector(object):
    """The main connector with the IRC world!

    It must only be used once!

    And it's __init__ won't connect to a server by itself. Use
    addconnectionsocket() function for this!"""

    def __init__(self):
        """Are you really willing to call this?

        I though this was called automatically when you started the
        class variable!"""

        self.connections = []
        self.loopthreads = []

        for n in xrange(len(self.connections)):
            self.loopthreads.append(Thread(target=self.mainloop, args=(n,)))

        for x in self.loopthreads:
            x.start()

    def addconnectionsocket(self,
                            server,
                            port=6667,
                            ident="GusPIRC",
                            realname="A GusPIRC Bot",
                            nickname="GusPIRC Bot",
                            password="",
                            email="email@address.com",
                            account_name="",
                            has_account=False,
                            channels=None,
                            authnumeric=001,
                            master=""):
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
        Result: connector.connections[index][4]!~ident_here@ip_here
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
        the both authing as soon as it succesfully connects to the network.

        - master: the name of the admin of the bot. ToDo: add tuple instead of string
        for multiple admins"""

        if not hasattr(channels, "__iter__"):
            raise TypeError("channels is not iterable!")

        log(u"Iteration check done!")

        # | The following commented-out code is known to be faulty and thus
        # | was commented out.

        # if socketindexbyaddress(server, port) != -1:
        #     log(u"Warning: Trying to append socket of existing address!"
        #     return False
        #
        # log(u"Check for duplicates done!"

        sock = socket(AF_INET, SOCK_STREAM)

        log(u"Socket making done!")

        sock.connect((server, port))

        log(u"Connected socket!")

        sock.sendall("USER %s * * :%s\r\n" % (ident, realname))
        if not has_account:
            sock.sendall("NICK %s\r\n" % account_name)
        else:
            sock.sendall("NICK %s\r\n" % nickname)

        log(u"Sent first commands to socket!")

        # function used for breaking through all loops
        def waituntilnotice():
            """This function is NOT to be called!
            It's a solution to the \"break only innerest loop\" problem!"""
            buffering = ""
            while True:
                x = sock.recv(1024).decode('utf-8')

                if x == "":
                    continue

                log(x)

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
                    y = x

                for z in y:
                    try:
                        compdata = z.split(" ")[1]
                    except IndexError:
                        continue
                    if compdata == str(authnumeric):
                        return

        waituntilnotice()

        log(u"NickServ Notice found!")

        if not has_account:
            sock.sendall("PRIVMSG NickServ :REGISTER %s %s\r\n" %
                         (password, email))
            sock.sendall("PRIVMSG Q :HELLO %s %s\r\n" % (email, email))
            log(u"Made account!")

        try:
            sock.sendall("AUTH %s %s\r\n" % (account_name, password[:10]))
        except IndexError:
            sock.sendall("AUTH %s %s\r\n" % (account_name, password))
        sock.sendall("PRIVMSG NickServ :IDENTIFY %s %s\r\n" %
                     (account_name, password))

        log(u"Authenticated!")

        if channels is None:
            channels = ("#%shelp" % nickname)
            log(u"Channel defaulting done!")
        else:
            log(u"Channel defaulting check done!")

        for x in channels:
            sock.sendall("JOIN %s\r\n" % x)

        log(u"Joined channels!")

        sock.setblocking(0)

        self.connections.append([sock, IterableQueue(), IterableQueue(),
                                 master, nickname, ident, server.split(".")[1]])

        log(u"Added to connections!")

        return True

    def mainloop(self, index):
        """It's the main loop mentioned in the docs.

        Call this in a while true loop, together with the rest!

        Parameters:
        - index: the index of the connector. Make sure you call this
        therefore in a for loop for each IRC server connection!

        Like, for example:

        for x in xrange(len(connector.connectors)):
            connector.mainloop(x)"""

        if not self.connections:
            return

        else:
            x = self.connections[index]
            buffering = ""
            log(u"Set buffering to none")

            y = []

            while True:

                w = ""

                try:
                    w = x[0].recv(4096).encode('utf-8')
                    log(u"Got message!")
                except error:
                    if len(self.connections[index][2]) > 0:
                        return
                    else:
                        continue

                if not (w.endswith("\n") or w.endswith("\r") or
                            w.endswith("\r\n")):
                    buffering = "%s%s" % (buffering, w)
                    continue

                if buffering != "":
                    w = "%s%s" % (buffering, w)

                y = w.split("\n")
                y.pop(-1)

                break

            for z in y:
                log(z)
                x[1].put(z.strip("\r"))
                if z.split(" ")[0] == "PING":
                    x[0].sendall("PONG :%s\r\n" % (z.split(":")[1]))
                    log(u"Sent PONG")

                try:
                    if z.split(" ")[0].strip(":") == "QUIT":
                        self.connections.pop(index)

                except IndexError:
                    pass

            log(u"Ended loop!")

    def relayoutqueue(self, index, messages):
        """Call this after mainloop() and after parsing each of
        receiveAllMessages() messages.

        Parameters:
        - index: the index of the OutQueue (abbreviated OQ)"""

        log(u"Sending OQ messages!")

        for x in messages:
            try:
                if x.split(":")[2].startswith("!"):
                    print "Command found!"  # mainly breakpoint fodder
            except IndexError:
                pass

        worked = False
        try:
            v = self.connections[index][2].get(False)
            if v == "":
                log(u"Error: Blank string in OQ!")
                return
            worked = True
            log(v)
            self.connections[index][0].sendall(v)
        except Empty:
            if not worked:
                log(u"No OQ messages sent! Wtf?")
            else:
                log(u"Sent all OQ messages!")
            pass

        sleep(0.5)

    def sendcommand(self, connectionindex=0, command=""):
        """Sends a command to the IRC server.

        - connectionindex: the index of the connection. Usually in the order
        you called addconnectionsocket().

        - command: the command string, including \":\" and \"PRIVMSG\" instead
        of \"MSG\" or \"SAY\". Don't include \"\\r\\n\", it's automatically added!"""
        self.connections[connectionindex][2].put("{0:s}\r\n".format(command))

    def sendmessage(self,
                    connectionindex=0,
                    target="ChanServ",
                    message="Error: No message argument provided to bot!"):
        """Sends a message to the target in the IRC server.

        - connectionindex: the index of the connection. Usually in the order
        you called addconnectionsocket().

        - target: the target. Usually a channel name (like #python) (replaces SAY)
        or a nickname (replaces MSG).

        Defaults to sending ChanServ commands for a good reason!

        - message: the message sent to the target. Self-explanatory, I hope."""
        self.connections[connectionindex][2].put_nowait("PRIVMSG %s :%s\r\n" %
                                                        (target, message))

    def disconnect(
            self,
            connectionindex=0,
            message="a GusPirc bot: The simplest Python low-level IRC interface"
    ):
        """Disconnects from the server in the index specified.

        - connectionindex: the index of the connection. Usually in the order
        you called addconnectionsocket().

        - message: the quit message. Self-explanatory."""
        self.connections[connectionindex][2].put_nowait("QUIT :%s\r\n") % (
            message)

    def receivelatestmessage(self, index=0):
        """Returns the last message from the queue of received messages from
        the IRC socket.

        - index: the index of the connection. Ususally in the order you called
        addconnectionsocket()."""
        try:
            return self.connections[index][1].get(False)
        except Empty:
            pass

    def sendnotice(self, index=0, noticetarget="", msg=""):
        """Sends a notice to noticetarget.

        Parameters:
        - index: the index of the connection. Usually in the order you called
        addconnectionsocket().

        - noticetarget: which channel or whom to send the notice to.

        - msg: the notice's message to send."""

        self.sendcommand(index, "NOTICE %s :%s" % (noticetarget, msg))

    def socketindexbyaddress(self, address, port=6667):
        """Returns the index of the IRC connection that is connected t
        address:port or -1 if there aren't any."""
        if self.connections:
            for x in self.connections:
                if tuple(x.getsockname()[:2]) == (address, port):
                    return self.connections.index(x)
        return -1

    def receiveallmessages(self, index=0):
        """Returns all the messages from the queue in the
        connection.

        - index: the index of the connection. Usually in the order you called
        addconnectionsocket()."""

        messages = []

        while True:

            try:
                log(u"Receiving message!")
                messages.append(self.connections[index][1].get(False))
            except Empty:
                log(u"Empty!")
                break

        return tuple(messages)
