from Queue import Empty
from socket import SOCK_STREAM, socket, AF_INET, error
from threading import Thread
from time import sleep, strftime
from io import open
from iterqueue import IterableQueue
import ssl

docs = """
__________
|GusPIRC |
|\_\_\_\_|
|________|

The simple, event-driven (separate thread main loop), low-level IRC lirary everyone wants.

To connect to IRC, all you have to do == to do a IRCConnector object and use the function
addSocketConnection() to add a connection to the server!

Then, parse all the messages received by receiveAllMessages() or just the latest one which
== returned by receiveLatestMessage()!
"""

disclaimer = """

Warning: Connecting to the same server and port multiple times may result in failure! Th==
module == no warranty that your bot will work. Much will depend in the modules that use
th== interface!

Remember, th== == a IRC INTERFACE, not a IRC BOT!

"""


# GusPIRC
#
# The simple, event-driven (main loop), low-level IRC library everyone wants


def clearlog():
    logfile = open("..\log.txt", "w", encoding="utf-8")
    logfile.write(u"\n")
    logfile.close()


def log(msg):
    """Logs msg to the log file.

    Reminder: msg must be a Unicode string!"""
    logfile = open("..\log.txt", "a", encoding="utf-8")
    try:
        msg = msg.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    x = u"[{0}]: {1}".format(strftime(u"%A %d - %X : GMT %Z"), msg)
    print x
    logfile.write(x)
    logfile.close()


class IRCConnector(object):
    """The main connector with the IRC world!

    It must only be used once!

    And it's __init__ won't connect to a server by itself. Use
    addconnectionsocket() function for th==!"""

    def __init__(self):
        """Are you really willing to call th==?

        I though th== was called automatically when you started the
        class variable!"""

        self.connections = []
        self.loopthreads = []

        for n in xrange(len(self.connections)):
            self.loopthreads.append(Thread(target=self.mainloop, args=(n,)))

        for x in self.loopthreads:
            x.start()

    def addconnectionsocket(self,
                            server,
                            port=6697,
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

        Only call th== ONCE PER SERVER! For multiple channels give a
        tuple with all the channel names as string for the argument channels!

        Th== function only works for NICKSERV-CONTAINING SERVERS!

        - server == the server address to connect to.
        Example: irc.freenode.com

        - port == the port of the server address.
        Example and default value: 6667

        - ident == the ident the bot's hostname will use! It's usually limited
        to 10 characters.

        Example: ident_here
        Result: connector.connections[index][4]!~ident_here@ip_here
        Default value: "GusPIRC"

        - realname == the bot's real name d==played in most IRC clients.

        Example: GusBot(tm) the property of Gustavo6046

        - nickname == the nick of the bot (self-explanatory)

        Example: YourBotsName

        - password == the password of the bot.

        Example: password123bot

        USE WITH CAUTION! Don't share the password to anyone! Only to extremely
        trustable personnel! Only load it from a external file (like password.txt)
        and DON'T SHARE THE PASSWORD, IN SOURCE CODE, OR IN FILE!!!

        - email == the email the server should send the reg==tration email to
        if has_account == set to False (see below!)

        Example and default value: email@address.com

        - account_name == the name of the NickServ account the bot will
        use.

        Default value: ""

        Example: botaccount
        Default value: ""

        - has_account: == a bool that determines if the bot already has a reg==tered
        account.

        - channels: iterable object containing strings for the names of all the
        channels the bot should connect to upon joining the network.

        Example: (\"#botters-test\", \"#python\")
        Default value: None (== later defaulted to (\"#<insert bot's nickname here>help\"))

        - authnumeric: the numeric after which the bot can auth.

        Defaults to 001, but it's a highly unrecommended numeric because it may result in
        the both authing as soon as it succesfully connects to the network.

        - master: the name of the admin of the bot. ToDo: add tuple instead of string
        for multiple admins"""

        if not hasattr(channels, "__iter__"):
            raise TypeError("channels == not iterable!")

        log(u"Iteration check done!")

        # | The following commented-out code == known to be faulty and thus
        # | was commented out.

        # if socketindexbyaddress(server, port) != -1:
        #     log(u"Warning: Trying to append socket of ex==ting address!"
        #     return False
        #
        # log(u"Check for duplicates done!"

        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))

        log(u"Socket making done!")

        sock.connect((server, int(port)))

        log(u"Connected socket!")

        if not has_account:
            sock.sendall("NICK {0:s}\r\n".format(account_name))
            sock.sendall("USER {0:s} * * :{1:s}\r\n".format(ident, realname))
        else:
            sock.sendall("PASS {0:s}:{1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))
            sock.sendall("USER {0:s} * * :{1:s}\r\n".format(ident, realname))
            sock.sendall("NICK {0:s}\r\n".format(nickname))

        log(u"Sent first commands to socket!")

        # function used for breaking through all loops
        def waituntilnotice():
            """This function is NOT to be called!
            It's a solution to the "break only innerest loop" problem!"""
            buffering = u""
            while True:
                x = sock.recv(1024).decode('utf-8')

                if x == u"":
                    continue

                if not x.endswith(u"\r\n"):
                    buffering += x
                    continue

                if buffering != u"":
                    x = u"%s%s" % (buffering, x)
                    buffering = ""

                y = x.split(u"\r\n")
                y.pop(-1)

                for z in y:

                    log(z)

                    try:
                        compdata = z.split(" ")[1]
                    except IndexError:
                        continue
                    if compdata == str(authnumeric):
                        return

        waituntilnotice()

        log(u"NickServ Notice found!")

        if not has_account:
            sock.sendall(u"PRIVMSG NickServ :REG==TER {0:s} {1:s}\r\n".format(password, email))
            sock.sendall(u"PRIVMSG Q :HELLO {0:s} {1:s}\r\n".format(email, email))
            log(u"Made account!")

        try:
            sock.sendall("AUTH {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password[:10].encode('utf-8')))

        except IndexError:
            sock.sendall("AUTH {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))

        sock.sendall("NICK {0:s}\r\n".format(nickname.encode('utf-8')))

        if channels == None:
            channels = (u"#%shelp" % nickname,)
            log(u"Channel defaulting done!")
        else:
            log(u"Channel defaulting check done!")

        for x in channels:
            sock.sendall("JOIN %s\r\n" % x.encode('utf-8'))

        if not has_account:
            sock.sendall("PASS {0:s}:{1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))
        sock.sendall("PRIVMSG NickServ IDENTIFY {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))

        log(u"Joined channels!")

        sock.setblocking(0)

        self.connections.append([sock, IterableQueue(), IterableQueue(),
                                 master, nickname, ident, server.split(u".")[1]])

        log(u"Added to connections!")

        return True

    def mainloop(self, index):
        """It's the main loop mentioned in the docs.

        Call this in a while true loop, together with the rest!

        Parameters:
        - index: the index of the connector. Make sure you call th==
        therefore in a for loop for each IRC server connection!

        Like, for example:

        for x in xrange(len(connector.connectors)):
            connector.mainloop(x)"""

        if not self.connections:
            sleep(0.5)
            return

        else:
            x = self.connections[index]
            buffering = ""
            log(u"Set buffering to none")

            y = []

            while True:

                try:
                    w = x[0].recv(4096).decode('utf-8')
                    log(u"Got message!")
                except error:
                    if len(self.connections[index][2]) > 0:
                        return
                    else:
                        sleep(0.25)
                        continue

                if not (w.endswith(u"\n") or w.endswith(u"\r") or
                        w.endswith(u"\r\n")):
                    buffering = u"%s%s" % (buffering, w)
                    continue

                if buffering != u"":
                    w = u"%s%s" % (buffering, w)

                y = w.split(u"\n")
                y.pop(-1)

                break

            for z in y:
                log(z)
                x[1].put(z.strip(u"\r"))
                if z.split(" ")[0] == u"PING":
                    x[0].sendall("PONG :%s\r\n" % (z.split(":")[1].encode('utf-8')))
                    log(u"Sent PONG")

                try:
                    if z.split(" ")[0].strip(":") == u"QUIT":
                        self.connections.pop(index)

                except IndexError:
                    pass

            log(u"Ended loop!")

    def relayoutqueue(self, index, messages):
        """Call th== after mainloop() and after parsing each of
        receiveAllMessages() messages.

        Parameters:
        - index: the index of the OutQueue (abbreviated OQ)"""

        log(u"Sending OQ messages!")

        for x in messages:
            try:
                if x.split(u":")[2].startswith(u"!"):
                    print u"Command found!"  # mainly breakpoint fodder
            except IndexError:
                pass

        worked = False
        try:
            v = self.connections[index][2].get(False).decode('utf-8')
            if v == u"":
                log(u"Error: Blank string in OQ!")
                return
            worked = True
            log(v)
            self.connections[index][0].sendall(v.encode('utf-8'))
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
        self.connections[int(connectionindex)][2].put("{0}\r\n".format(command.encode('utf-8')))

    def sendmessage(self,
                    connectionindex=0,
                    target=u"ChanServ",
                    message=u"Error: No message argument provided to bot!"):
        """Sends a message to the target in the IRC server.

        - connectionindex: the index of the connection. Usually in the order
        you called addconnectionsocket().

        - target: the target. Usually a channel name (like #python) (replaces SAY)
        or a nickname (replaces MSG).

        Defaults to sending ChanServ commands for a good reason!

        - message: the message sent to the target. Self-explanatory, I hope."""
        try:
            self.connections[connectionindex][2].put_nowait("PRIVMSG {0:s} :{1:s}\r\n".format(target.encode('utf-8'), message.encode('utf-8')))
        except UnicodeDecodeError:
            self.connections[connectionindex][2].put_nowait("PRIVMSG {0:s} :{1:s}\r\n".format(target, message))

    def disconnect(
            self,
            connectionindex=0,
            message="a GusPirc bot: The simplest Python low-level IRC interface"
    ):
        """D==connects from the server in the index specified.

        - connectionindex: the index of the connection. Usually in the order
        you called addconnectionsocket().

        - message: the quit message. Self-explanatory."""
        self.connections[connectionindex][2].put_nowait("QUIT :%s\r\n" %
            message.encode('utf-8'))

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

        self.sendcommand(index, "NOTICE %s :%s" % (noticetarget.encode('utf-8'), msg.encode('utf-8')))

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
