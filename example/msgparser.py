# This is a hugely improved and GusPIRC-adaptated (in other words, HEAVILY MODIFIED) version
# of Victor Vortex bot by OldCoder and mrtux.

from argparse import ArgumentError
from importlib import import_module
from json import dump, load
from skcipher import NonAsciiMsgError, NotEnoughCharactersInKeyError, ciphermsg
from google import search
from wikipedia import summary, search
from guspirc import log
from UserDict import UserDict
from random import choice

class GusBotException(BaseException):
    pass

class NotLoggedInException(GusBotException):
    pass

class NoPermsException(GusBotException):
    pass

class LoggedUsers(UserDict):
    def __getattr__(self, key):
        try:
            return self.__getitem__[key]
        except KeyError:
            raise NotLoggedInException(key)

class Permlevels(UserDict):
    def __getattr__(self, key):
        try:
            return self.__getitem__[key]
        except KeyError:
            raise NoPermsException(key)

def parsemsg(ircmsg, connection, index, tre, modules, wiki, permlevels, accounts, loggedusers):
    log(u"Parsing message!")

    replies = {
        "hey GusBot|hey, GusBot": "But |, what did I do?",
        "wtf GusBot": "What's wrong, |?",
        "so bad|so sad|got worse": "Trust me |! I'm sure it'll get better!",
        "fuck you GusBot": "Don't piss me off, |!",
        "pants": "Someone said pants? Lol!",
        "GusBot, my son": "But |, am I your son?",
        "GusBot, are you a bot|is GusBot a bot|is GusBot your bot":
            "I'm probably the first bot to ever admit is a bot, dear |. Have a good day.",
        "owns GusBot": "Hey |, my owner is Gustavo6046!",
        "but, GusBot": "What's up, |?",
        "but GusBot!": "Yes, it's it!",
        "why, GusBot?": "because it's the truth, |",
        "when?": "Someday.",
        "tell me, GusBot|tell me GusBot": "I can't!",
        "tell GusBot": "I don't want to listen to him |, thanks",
        "Hey, listen|hey listen": "I won't!",
        "Beaten Xaero?": "Yes but beating Xan is funner: ut99.org",
        "fuck GusBot": "Hey!",
        "GusBot is a freak": "Why? :(",
        "GusBot is shit": "Yes, from your ass! Lol",
        "why would GusBot": "Because yeah, it's not so bad. For me."
    }
    replies.update({
        "Please don't, GusBot|Please no GusBot|please no, GusBot":
            "Yes, yes, yes! >:)",
        "i'm sick": "Ohhh, you'll get better :^)",
        "yes GusBot|yes, GusBot": "No, GusBot!",
        "no GusBot|no, GusBot": "yes GusBot",
        "finally, GusBot": "Yes, I'm so slow |!"
    })
    replies.update(
        {"heil": "No, I'm a nazi killer! *shoots lasers at | from eyes*",
         "die GusBot": "No, you! *shoots with a bazooka at |",
         "no, you, GusBot|no you GusBot|no, you GusBot|no you, GusBot":
             "no, you, |!",
         "Reloading": "Reloaded, |? Now shoot him!",
         "shoots": "*shoots back at |*",
         "motherfucker": "No |, it's YOU! | IS the motherfucker!"})
    replies.update({"faggot":
                        "No, you |, not him, or even me, despite my dumbass!",
                    "lol":
                        "olo",
                    "mwah":
                        "Oh no, | is evil! FIRE!",
                    "...":
                        "Think, |, think!",
                    "GusBot, freak out now! Passwordx   : LUABRASIL":
                        "HEYA PUSSIES | IS THE KING NOW !! YEAH EASTER EGG UNLEASHED !!! WOOOO\r\nTHIS IS AWESOME!!!!!!!!!"})

    insults = ("Fuck you |!", "| is shit!", "Hey, | should go to hell!",
               "| is a MOTHER MOTHER FUCKER!",
               "I shouldn't have motivated | aka Mr Fucked Man!",
               "Why is | so confident? That bitch!", "Die |!",
               "What the fuck, |! Go to fucking Hell!", "| is scum!",
               "The Pope hates you, |!",
               "I'm sure they'll fuck | until he\'s dry of sperma!",
               "| IS NIGGA",
               "| IS BLACK",
               "FUCKING PILE OF |GGING CRAPPY SHIT",
               "ME :shoots at | with every arsenal in Universe",
               "| is a Terrible Terry Worse than Hitler",
               "| be killed by Hitler in a Neo Holocaust!",
               "| will be fucked up!",
               "| became Romero's bitch!",
               "I'm sure | is my cock.")

    prehopes = (
        "Life is a illusion named delusion but", "Don\'t feel bad",
        "Why are you sad", "So you will quit? But", "So bad you feel bad",
        "Why all that crying",
        "Since when did you quit for something? Tell me please; after all",
        "Don't give up now that you\'re so close; because",
        "FUCK YOU CRYING! There are REASONS to curse your crying; including")

    hopes = (
        "I\'m sure some day you can do it", "you will win this time",
        "you can do it, you can do it",
        "there are so many good things in the world to be happy about",
        "you are always so pessimist",
        "you can do it with some hard work, but it\'s not too much",
        "I promise you you will succeed some day",
        "if you do so your mother will try to give you milk to calm you down",
        "you might end up in a maze of depression",
        "this would be a dishonor for your friends that always try to help you",
        "you must be motivated, and I know the best ways of doing so! There I go to help you",
        "there is more good than bad in this story",
        "why all this crying? There is so much Coke to drink",
        "isn't it cool what you are trying to achieve? Now go and continue it!"
    )
    hopes = hopes + (
        "this world isn\'t so cruel, trust me",
        "when you succeed, you will look at the crying past and laugh from your cries",
        "you can battle the hordes now that I gave you the bazooka",
        "that\'s pure cringe and waste of time when you should be stepping closer from success",
        "success is close, so close I guess you just reached it")

    for x in modules:
        try:
            tre, modules, wiki, permlevels, accounts, loggedusers = getattr(import_module(x), "parsemsg")(tre, modules,
                                                                                                          wiki,
                                                                                                          permlevels,
                                                                                                          accounts,
                                                                                                          loggedusers)

        except AttributeError:
            pass

            # detects message details
    try:
        msgargs = u":".join(ircmsg.split(u":")[2:]).split(u" ")
        msgchan = ircmsg.split(u" ")[2]
        msgmode = ircmsg.split(u" ")[1]
        msgtarget = ircmsg.split(u" ")[3]
        msgsrc = ircmsg.split(u" ")[0].strip(u":")
        msgnick = ircmsg.split(u" ")[0].split(u"!")[0].strip(u":")
        msgident = ircmsg.split(u"!")[1].split(u"@")[0]
        msghost = ircmsg.split(u"@")[1].split(u" ")[0]
    except IndexError:
        pass  # ignore the message for now

    try:

        if msgtarget == "GusBot" and msgmode == "KICK":
            connection.sendcommand(index, "JOIN {0}".format(msgchan))

        if not "PRIVMSG" == msgmode:
            return tre, modules, wiki, permlevels, accounts, loggedusers

        log(u"%s %s %s :%s" % (msgsrc, msgmode, msgchan, msgargs))

    except UnboundLocalError:
        return tre, modules, wiki, permlevels, accounts, loggedusers

    try:
        if msgnick == "Gustavo6046":
            accounts["BotOwner"] = open("password.txt").read()
            loggedusers["Gustavo6046"] = "BotOwner"
            permlevels["BotOwner"] = 99999
    except UnboundLocalError:
        pass

    if "ERROR" == msgmode or ("QUIT" == msgmode and connection.connections[
        index][4] == ircmsg.msgargs(" ")[0].strip(":")):
        return False

    try:

        # parses fake message from IRC protocol
        if "!parse" == msgargs[0].lower():
            try:
                return parsemsg(" ".join(msgargs[1:]), connection, index, tre, modules, wiki, permlevels, accounts, loggedusers)
            except IndexError:
                connection.sendmessage(index, msgnick, "{0}: No message to parse!".format(msgnick))

        if "!say" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            connection.sendmessage(index, msgchan, " ".join(msgargs[1:]))
            connection.sendmessage(index, connection.connections[index][3],
                                   u"Message sent: {0:s}".format(" ".join(msgargs[1:])))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # insults >:)
        if msgargs[0].lower() == "!insult" and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            try:
                connection.sendmessage(
                    index, msgchan,
                    choice(insults).replace("|", " ".join(msgargs[1:])))
            except IndexError:
                connection.sendmessage(
                    index, msgchan,
                    "{0}: Error, not enough arguments!".format(msgnick))

        # cleans Markov.. .all of it
        if "!clearmarkov" == msgargs[0].lower():
            tre = {}
            connection.sendmessage(index, msgchan, "{0}: Cleared all of Markov!".format(msgnick))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # parses markov from file
        if "!parsemarkovfile" == msgargs[0] and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:

            for x in msgargs[1:]:

                try:
                    markov_file = open("{0}.markov".format(x))

                except IOError:
                    connection.sendmessage(index, msgchan, "{0}: No such file!".format(msgnick))
                    return None

                else:
                    for z in markov_file.read().split("\n"):

                        z = z.split(" ")

                        for x in xrange(len(z)):

                            if z[x - 1] == z[x]:
                                continue

                            try:
                                try:
                                    tre[z[x - 1].lower()].append(z[x].lower())
                                except KeyError:
                                    tre[z[x - 1].lower()] = [z[x].lower()]

                            except IndexError:
                                continue

            connection.sendmessage(index, msgchan, "{0}: Parsed succesfully!".format(msgnick))

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # adds messages to Markov dictionary
        if not (msgargs[0].lower().startswith(u"!") and msgsrc != u"{0:s}!~{1:s}@unnafiliated/{2:s}".format(connection.connections[index][4], connection.connections[index][5], connection.connections[index][4])):

            for x in xrange(len(msgargs)):

                if msgargs[x - 1] == msgargs[x]:
                    continue

                try:
                    try:
                        tre[msgargs[x - 1].lower()].append(msgargs[x].lower())
                    except KeyError:
                        tre[msgargs[x - 1].lower()] = [msgargs[x].lower()]
                except IndexError:
                    continue

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # joins a network
        if "!connect" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 3:
            try:
                connection.addconnectionsocket(
                    server=msgargs[1],
                    port=msgargs[2],
                    ident=msgargs[3],
                    realname=u"GusBot(tm) the property of Gustavo6046",
                    nickname=u"GusBot",
                    password=msgargs[4],
                    email=u"gugurehermann@gmail.com",
                    account_name=u"GusBot",
                    has_account=True,
                    channels=tuple(msgargs[6:]),
                    authnumeric=int(msgargs[5]))
            except IndexError:
                connection.sendmessage(
                    index, msgchan, "%s: Not enough arguments!" % (msgnick,))


                # kickes someone
        if "!kick" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            try:
                kickmsg = u":".join(u" ".join(msgargs).split(u":")[1:])
                connection.sendmessage(index, message="OP {0}".format(msgchan))
                for x in msgargs[1:]:
                    connection.sendcommand(index, "KICK {0} {1} :{2}".format(msgchan, x, kickmsg))
                connection.sendmessage(index, message="DEOP {0}".format(msgchan))
            except IndexError:
                connection.sendmessage(index, message="DEOP {0}".format(msgchan))
                connection.sendmessage(index, msgchan, "{0}: Not enough arguments!".format(msgnick))

                # handles channel parting and joining
        if "!join" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:
            if len(msgargs) < 2:
                connection.sendmessage(index, msgchan,
                                       "Invalid number of arguments!")
            try:
                for x in msgargs[1:]:
                    connection.sendcommand(index, "JOIN {0:s}".format(x))
            except IndexError:
                connection.sendcommand(index, "JOIN %s" % (msgargs[1]))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        if "!part" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:
            if len(msgargs) < 2:
                connection.sendmessage(index, msgchan,
                                       "Invalid number of arguments!")
                return tre, modules, wiki, permlevels, accounts, loggedusers
            try:
                connection.sendcommand(index, "PART %s :%s" %
                                       (msgargs[1], " ".join(msgargs[2:])))
            except IndexError:
                connection.sendcommand(index, "PART %s" % (msgargs[1]))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # Search for topic in Wikipedia

        if "!searchwiki" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            wiki = search(" ".join(msgargs[1:]))
            if not wiki:
                connection.sendmessage(
                    index, msgchan,
                    "%s: No page found for search term \'%s\'!" % (
                        msgnick, " ".join(msgargs[
                                          1:])))
            else:
                wikistr = ""
                for x in wiki:
                    if wikistr == "":
                        wikistr = x
                    else:
                        wikistr = "%s, %s" % (wikistr, x)
                connection.sendmessage(index, msgchan,
                                       "%s: Search succesful: %s" %
                                       (msgnick, wikistr))
                return tre, modules, wiki, permlevels, accounts, loggedusers

        if "!getwiki" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            if not wiki:
                connection.sendmessage(
                    index, msgchan,
                    "%s: No wikipages avaiable Use: \'!searchwiki\'!" % (
                        msgnick,))
            else:
                wikistr = ""
                for x in wiki:
                    if wikistr == "":
                        wikistr = x
                    else:
                        wikistr = "%s, %s" % (wikistr, x)
                connection.sendmessage(index, msgchan, "%s: Pages avaiable: %s"
                                       % (msgnick, wikistr))
                return tre, modules, wiki, permlevels, accounts, loggedusers

        if "!wikiread" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                for x in summary(wiki[int(msgargs[1]) + 1],
                                 sentences=int(msgargs[2])).split("\n"):
                    connection.sendmessage(index, msgnick, x)
            except IndexError:
                if not wiki:
                    connection.sendmessage(
                        index, msgchan,
                        "%s: Search first to cache the results!" % (msgnick,))
                else:
                    try:
                        msgargs[2]
                    except IndexError:
                        connection.sendmessage(
                            index, msgchan,
                            "%s: Less than 2 arguments given!" % (msgnick,))
                    else:
                        connection.sendmessage(index, msgchan,
                                               "%s: Incorrect wikipage index!" %
                                               (msgnick,))

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # Gets Google URL for a page in a topic

        if "!googlepage" == msgargs[0].lower() and permlevels[loggedusers[msgnick]] >= 0:
            try:
                connection.sendmessage(index, msgnick, "Found pages:\r\n ")
                page = search(query=msgargs[1])
                for x, i in enumerate(page, start=1):
                    connection.sendmessage(index, msgnick, "{0}: {1}".format(x, i))
            except IndexError:
                connection.sendmessage(index, msgchan,
                                       "%s: No argument given!" % (msgnick,))

                # Responds to varied messages

        if "hi GusBot".lower() in " ".join(msgargs).lower(
        ) or "hello GusBot" in " ".join(msgargs):
            connection.sendmessage(index, msgchan,
                                   "Hello %s! Have a good day!" % (msgnick,))

        if "bye GusBot".lower() in " ".join(msgargs).lower():
            connection.sendmessage(index, msgchan,
                                   "Goodbye %s! Be God with you!" % (msgnick,))


        try:
            for z in replies.keys():
                for x in z.decode('utf-8').split("|"):
                    if x.lower() in u" ".join(msgargs).lower() and msgnick != u"GusBot" and u"GusBot".lower() in u" ".join(
                            msgargs).lower():
                        connection.sendmessage(index, msgchan, replies[
                            z].replace("|", msgnick))
        except (KeyError, UnboundLocalError, IndexError):
            return None

        # reply list
        if "!replies" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            connection.sendmessage(index, msgnick, "Replies:")
            connection.sendmessage(index, msgnick, " ")
            for x in sorted(replies.keys()):
                for z in x.split("|"):
                    connection.sendmessage(index, msgnick,
                                           "\"{0}\" = \"{1}\"".format(
                                               z, replies[x].replace("|",
                                                                     msgnick)))

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # loads module as a plugin
        if "!loadplugin" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                import_module("plugins.%s" % (msgargs[1]))
                modules.append(msgargs[1])
            except IndexError:
                connection.sendmessage(
                    index, msgchan, "%s: Not enough arguments!" % (msgnick,))
            except ImportError:
                connection.sendmessage(index, msgchan,
                                       "%s: Error, no module \"%s\" found!" %
                                       (msgnick, msgargs[1]))
            else:
                connection.sendmessage(
                    index, msgchan, "%s: Module \"%s\" imported succesfully!" %
                                    (msgnick, msgargs[1]))

                # do some plugin action
        if "!execplugin" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                result = str(eval("%s.parse(%s)" % (msgargs[1], ", ".join(
                    msgargs[2:]))))
                connection.sendmessage(index, msgchan, result)
            except IndexError:
                connection.sendmessage(
                    index, msgchan,
                    "%s: Not enough arguments! (expected 2 or more, 1 for the module name and 2 for the parse argument)"
                    % (msgnick,))
            except (ValueError, ArgumentError):
                connection.sendmessage(index, msgchan,
                                       "{0:s}: Invalid arguments given!".format(msgnick, ))
            except NameError:
                connection.sendmessage(
                    index, msgchan,
                    "{0:s}: Some NameError executing the plugin parser!".format(msgnick, ))

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # logs off
        if "!logout" == msgargs[0].lower():

            try:
                del loggedusers[msgnick.encode("utf-8")]
                connection.sendmessage(index, msgchan, "{0}: Logged out succesfully!".format(msgnick))

            except KeyError:
                connection.sendmessage(index, msgchan, "{0}: You're not even logged!".format(msgnick))

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # tells loaded plugins
        if "!plugins" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            pluginstr = ""

            for x in modules:
                if pluginstr == "":
                    pluginstr = x
                else:
                    pluginstr = "%s, %s" % (pluginstr, x)

            connection.sendmessage(index, msgchan,
                                   "%s: Plugins are: %s" % (msgnick, pluginstr))

            return tre, modules, wiki, permlevels, accounts, loggedusers

            # Calculates factorial
        if "!factorial" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                msgargs[1]
            except IndexError:
                connection.sendmessage(index, msgchan,
                                       "%s: No argument given!" % msgnick)

            else:

                if msgargs[1] < 0:
                    n = -1
                else:
                    n = 1

                for i in xrange(n, int(msgargs[1])):
                    if i < 0:
                        i *= -1
                    n *= i
                    log(u"Part %i reached!" % (i,))

                connection.sendmessage(index, msgchan, "%s: %s! is %i." %
                                       (msgnick, msgargs[1], n))

        # gives someone motivation
        if "!hope" == msgargs[0] and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                connection.sendmessage(index, msgchan,
                                       "{0:s}: {1:s}, {2:s}!".format(msgargs[1], choice(prehopes), choice(hopes)))
            except IndexError:
                connection.sendmessage(index, msgchan, "{0:s}: No argument given!".format(msgnick))

        # Secret kick
        if "!secretkick" == msgargs[0] and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            try:
                connection.sendmessage(index, message="OP {0}".format(msgchan))
                for x in msgargs[1:-1]:
                    connection.sendcommand(index, "KICK {0} {1}".format(msgchan, ciphermsg(msgargs[-1], x)))
                connection.sendmessage(index, message="DEOP {0}".format(msgchan))

            except IndexError:
                connection.sendmessage(index, msgchan, "{0}: Not enough arguments!".format(msgnick))

            except NotEnoughCharactersInKeyError:
                connection.sendmessage(index, msgchan, "{0}: The key does not have all ASCII characters!")

            except NonAsciiMsgError:
                connection.sendmessage(index, msgchan,
                                       "{0}: Currently only ASCII is supported. However you can use Unicode in the key!")

        # Help message
        if "!commands" == msgargs[0].lower() or "!help" == msgargs[0].lower() or "!list" == msgargs[0].lower() and \
                        permlevels[loggedusers[msgnick.encode("utf-8")]] >= -1:
            connection.sendmessage(index, msgnick, "Commands:")
            connection.sendmessage(index, msgnick, " ")
            connection.sendmessage(
                index, msgnick,
                "!sayabout topic : Say stuff based on the topic (2)")
            connection.sendmessage(index, msgnick,
                                   "!owner . . . . .: Tells who owns this bot")
            connection.sendmessage(
                index, msgnick,
                "!nick . . . . . : Changes the bot's nickname (11)")
            connection.sendmessage(
                index, msgnick,
                "!savedefs . . . : Saves the current lexical tre in owner's HDD (12)")
            connection.sendmessage(
                index, msgnick,
                "!wordcount . . .: How many words are there in the Markov list?")
            connection.sendmessage(
                index, msgnick,
                "!loaddefs . . . : Loads the lexical tre from file in owner's HDD (12)")
            connection.sendmessage(
                index, msgnick,
                "!raw . . . . . .: Executes a IRC command. (1)")
            connection.sendmessage(
                index, msgnick, "!flushqueue . . : Flushes message queue. (2)")
            connection.sendmessage(
                index, msgnick,
                "!join and !part : Joins and parts channels respectively")
            connection.sendmessage(
                index, msgnick,
                "!plugins . . . .: Shows which plugins are loaded.")
            connection.sendmessage(
                index, msgnick,
                "!searchwiki . . : Searches for some query in Wikipedia, up to n results. (3)")
            connection.sendmessage(
                index, msgnick,
                "!getwiki . . . .: Get search results index from Wikipedia. (3)")
            connection.sendmessage(
                index, msgnick,
                "!wikiread . . . : Read the article in the index from the wikilist. (3)")
            connection.sendmessage(
                index, msgnick,
                "!googlepage . . : Searches Google for pages using a query. (3)")
            connection.sendmessage(index, msgnick,
                                   "!loadplugin . . : Loads a plugin.")
            connection.sendmessage(
                index, msgnick,
                "!execplugin . . : Shows the return value of plugin's parse(args...) as a string, where args..."
                "are command arguments (except the first argument which is the plugin name)")
            connection.sendmessage(index, msgnick,
                                   "!quit . . . . . : Leaves the network (13)")
            connection.sendmessage(
                index, msgnick,
                "!regaccount . . : Registers a account in the system based on your hostname and ident")
            connection.sendmessage(
                index, msgnick,
                "!myaccount . . .: Shows the name of your current account")
            connection.sendmessage(
                index, msgnick,
                "!perms . . . . .: Changes the permission level of someone (12)")
            connection.sendmessage(
                index, msgnick,
                "!showperms . . .: Shows the permission level of the ident and hostname (11)")
            connection.sendmessage(
                index, msgnick,
                "!myperms . . . .: Shows the permission level of the command caller")
            connection.sendmessage(
                index, msgnick,
                "!factorial . . .: Calculates the factorial of a number (2)")
            connection.sendmessage(
                index, msgnick,
                "This bot will also reply to normal phrases and replies.")
            connection.sendmessage(index, msgnick, " ")
            connection.sendmessage(
                index, msgnick,
                "(1x) means the command is only for people with permission level equal or greater than x.")
            connection.sendmessage(
                index, msgnick,
                "(2) means the command isn't currently working correctly.")
            connection.sendmessage(
                index, msgnick,
                "(3) means the command isn't tested. Use it on your own risk!")
            connection.sendmessage(index, msgnick, " ")
            connection.sendmessage(
                index, msgnick,
                "For more info refer to irc.freenode.net #gusbot")
            return tre, modules, wiki, permlevels, accounts, loggedusers

        ## Account System ##


        # Tells someone's permission level
        if "!showperms" == msgargs[0] and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:

            try:
                theaccount = loggedusers[msgargs[1]]

                if theaccount == "Guest":
                    connection.sendmessage(index, msgchan,
                                           u"{0:s}: {1} is in a guest account!!".format(msgnick, msgargs[1]))

                else:
                    connection.sendmessage(index, msgchan,
                                           "{0:s}: {1}'s permission level is {2}.".format(msgnick, msgargs[1],
                                                                                          permlevels[
                                                                                              accounts[msgargs[1]]]))

            except IndexError:
                connection.sendmessage(index, msgchan, "{0}: Not enough arguments!".format(msgnick))

            except KeyError:
                connection.sendmessage(index, msgchan, "{0}: {1} has no account!".format(msgnick, msgargs[1]))

        # Tells someone's account
        if "!myaccount" == msgargs[0]:

            try:
                theaccount = loggedusers[msgnick.encode("utf-8")]

                if theaccount == "Guest":
                    connection.sendmessage(index, msgchan, u"{0:s}: You have a guest account!".format(msgnick))

                else:
                    connection.sendmessage(index, msgchan, "{0:s}: Your account is {1:s}.".format(msgnick, theaccount))

            except KeyError:
                connection.sendmessage(index, msgchan, "{0}: You have no account!".format(msgnick))

        # Registers an account
        if "!regaccount" == msgargs[0]:

            if msgchan != "GusBot":
                connection.sendmessage(index, msgnick, "To register an account please privately message the bot!")
                return None

            try:
                if hasattr(accounts, msgargs[1]):
                    connection.sendmessage(index, msgnick, "The account already exists!")
                    return None
                else:
                    accounts[msgargs[1]] = msgargs[2]
                    permlevels[msgargs[1]] = 0
                    connection.sendmessage(index, msgnick, "Account registered succesfully!")

            except IndexError:
                connection.sendmessage(index, msgchan,
                                       "{0}: Not enough arguments! One argument for acc ount name, other for password!")

            return tre, modules, wiki, permlevels, accounts, loggedusers

        if "!identify" == msgargs[0].lower():
            log(u"Identification attempt discovered!")
            try:
                if msgchan != "GusBot":
                    connection.sendmessage(index, msgnick,
                                           "{0}: To identify please send a private message to the bot.".format(msgnick))
                    return None

                elif accounts[msgargs[1]] == msgargs[2]:
                    loggedusers[msgnick.encode("utf-8")] = msgargs[1]
                    connection.sendmessage(index, msgnick, "{0}: Logged in succesfully!".format(msgnick))
                    return tre, modules, wiki, permlevels, accounts, loggedusers

                else:
                    connection.sendmessage(index, msgnick, "{0}: Invalid password!".format(msgnick))
                    return None

            except KeyError:
                connection.sendmessage(index, msgnick, "{0}: Invalid account name!".format(msgnick))

            except IndexError:
                connection.sendmessage(index, msgnick, "{0}: Not enough arguments!".format(msgnick))

            return None

        # tells who is the owner
        if "!owner" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            connection.sendmessage(index, msgchan, "My owner is: %s" %
                                   (connection.connections[index][3]))
            return tre, modules, wiki, permlevels, accounts, loggedusers

            # shows your permlevel
        if "!myperms" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            try:
                connection.sendmessage(index, msgchan, "{0:s}: Your permlevel is {1:d}.".format(msgnick, permlevels[
                    loggedusers[msgnick.encode("utf-8")]]))
            except KeyError:
                connection.sendmessage(index, msgchan, "{0}: You have no account!".format(msgnick))

        # word count\
        if "!wordcount" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            connection.sendmessage(index, msgchan,
                                   "There are %i words." % (len(tre.keys())))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # change someone's permlevels
        if "!perms" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:

            try:
                permlevels[accounts[msgargs[1]]] = int(msgargs[2])

            except IndexError:
                connection.sendmessage(index, msgchan,
                                       "%s: Not enough arguments!" %
                                       msgnick)

            except ValueError:
                connection.sendmessage(index, msgchan,
                                       "%s: Wrong values for arguments!" %
                                       msgnick)

            except KeyError:
                connection.sendmessage(index, msgchan,
                                       "%s: %s has no account!" % (
                                           msgnick, str(msgargs[1])))

            else:
                connection.sendmessage(
                    index, msgchan,
                    "%s: %s's permission level set to %i!" % (
                        msgnick, str(msgargs[1]), int(msgargs[2])))

                # change nick
        if "!nick" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            connection.sendcommand(index, "NICK %s" % (msgargs[1]))
            connection.sendmessage(index, msgchan,
                                   "Nick changed to %s." % (msgargs[1]))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # quits the network
        if "!quit" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            try:
                connection.disconnect(index, " ".join(msgargs[1:]))
            except IndexError:
                connection.disconnect(index)
            return False

        # say about some topic
        if "!sayabout" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:
            if len(msgargs) < 2:
                connection.sendmessage(index, msgchan, "{0}: What topic?".format(msgnick))
            else:
                try:
                    x = msgargs[1].lower()
                    tre[msgargs[1].lower()] = tre[msgargs[1].lower()]

                except KeyError:
                    connection.sendmessage(index, msgchan, "{0}: Not such a topic, sorry!".format(msgnick))

                else:
                    phrase = msgargs[1].lower()
                    i = 0

                    while True:
                        debuginfo = u"{0}: {1}".format(x, phrase)
                        i += 1

                        try:
                            x = choice(tre[x])
                            if x == phrase.split(" ")[-1]:
                                raise RuntimeError
                            if i > 99:
                                raise RuntimeError
                        except (KeyError, RuntimeError):
                            connection.sendmessage(index, msgchan, u"{0}: {1}".format(msgnick, phrase).encode("utf-8"))
                            break

                        phrase = u"{0} {1}".format(phrase, x)

                        del debuginfo

            return tre, modules, wiki, permlevels, accounts, loggedusers

        # saves current Markov chain
        if "!savedefs" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 1:
            if len(msgargs) < 2:
                connection.sendmessage(index, msgchan, "Not enough arguments!")
            treefile = open("treedefs\\{0:s}.dict".format(msgargs[1]), "w")
            dump(tre, treefile)
            connection.sendmessage(index, msgchan,
                                   "Sent to file %s with success!" %
                                   (msgargs[0].lower()))
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # some few Hope :D
        if ":(" in " ".join(msgargs) or ":C" in " ".join(msgargs) or (
                        ":/" in " ".join(msgargs) and not "http" in " ".join(msgargs)
        ) or ":'(" in " ".join(msgargs) or ":\\" in " ".join(msgargs):
            connection.sendmessage(index, msgchan,
                                   "%s: %s, %s!" % (msgnick, choice(prehopes),
                                                    choice(hopes)))

        # loads current Markov chain
        if "!loaddefs" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:
            if len(msgargs) == 0:
                connection.sendmessage(index, msgchan,
                                       "No argument given! Aborting...")
                return tre, modules, wiki, permlevels, accounts, loggedusers
            tre = load(("treedefs\\%s.txt" % msgargs[1].lower(), "r"), 'utf-8')
            connection.sendmessage(index, msgchan, "No argument given! Aborting...")
            return tre, modules, wiki, permlevels, accounts, loggedusers

        # executes command
        if "!raw" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 2:
            connection.sendcommand(index, " ".join(msgargs[1:]))

        # flushes the command queue
        if "!flushqueue" == msgargs[0].lower() and permlevels[loggedusers[msgnick.encode("utf-8")]] >= 0:

            flusheditems = len(connection.connections[index][1])

            if flusheditems == 0:
                connection.sendmessage(index, msgchan,
                                       "%s: No message to flush!" % msgnick)
                return None

            connection.sendmessage(index, msgchan,
                                   "{0:s}: Flushed {1:d} messages and IRC commands.".format(msgnick, flusheditems))
            log(u"Flushed %i messages and IRC commands." % flusheditems)
            savemsgs = []
            savemsgstr = ""

            for i in connection.connections[index][1]:
                if i is None:
                    continue

                if "PONG" == i.split(" ")[0] or "NickServ" == i.split(" ")[
                    2] or "ChanServ" == i.split(" ")[2]:
                    savemsgs.append(i)
                    print("Saved {0}!".format(i))
                    savemsgstr = "{0}, {1}".format(savemsgstr, i)

            connection.connections[index][1].set_to_iterator(savemsgs)

            log(u"New queue after flush: [%s]" % (savemsgstr.strip("\r\n"),))

            return None

    except NoPermsException:
        try:
            if loggedusers[msgnick.encode("utf-8")] == "Guest":
                permlevels[loggedusers[msgnick.encode("utf-8")]] = -1
            else:
                accounts["Guest"] = ""
                loggedusers[msgnick.encode("utf-8")] = "Guest"
                permlevels["Guest"] = -1
                connection.sendmessage(
                    index, msgchan,
                    "%s: You're not registered! You're bound to a guest account until you register now."
                    % (msgnick,))

        except (KeyError, NoPermsException):
            accounts["Guest"] = ""
            loggedusers[msgnick.encode("utf-8")] = "Guest"
            permlevels["Guest"] = -1
            connection.sendmessage(
                index, msgchan,
                "%s: You're not registered! You're bound to a guest account until you register now."
                % (msgnick,))
        except UnboundLocalError:
            return None

        return parsemsg(ircmsg, connection, index, tre, modules, wiki, permlevels, accounts, loggedusers)

    except (NotLoggedInException, KeyError):
        accounts["Guest"] = ""
        loggedusers[msgnick.encode("utf-8")] = "Guest"
        permlevels["Guest"] = -1
        connection.sendmessage(
            index, msgchan,
            "%s: You're not registered! You're bound to a guest account until you register now."
            % (msgnick,))

        return parsemsg(ircmsg, connection, index, tre, modules, wiki, permlevels, accounts, loggedusers)

    return tre, modules, wiki, permlevels, accounts, loggedusers
