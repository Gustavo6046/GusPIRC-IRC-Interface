class MarkovKeyword(object):

    def __init__(self, thiskeyword):
        self.thiskeyword = thiskeyword
        self.nextkeywords = []

    def __iter__(self):
        return self.nextkeywords

    def getnextword(self):
        return choice(nextkeywords)

    def addkeyword(self, other):
        self.nextkeywords.append(MarkovKeyword(other))

class MarkovChain(object):

    def addmarkovkeyword(self, before, name, next_):
        found = False
        pkw = None

        if before == name:
            return

        for x in self.allwords:
            if x.thiskeyword == before:
                nkw = MarkovKeyword(name)
                self.allwords.append(nkw)
                x.nextkeywords.append(nkw)
                found = True
            if x.thiskeyword == next_:
                pkw = MarkovKeyword(name)
                self.allwords.append(pkw)
                pkw.nextkeywords.append(x)

        if found == False:
            nkw = MarkovKeyword(name)
            self.keywords.append(nkw)
            self.allwords.append(nkw)
            self.keywords.append(pkw)

    def __init__(self):
        self.keywords = []
        self.allwords = []

    def composephrase(self, starter):
        found = None
        for x in self.allwords:
            if x.thiskeyword == starter:
                found = x

        if found == None:
            return None

        i = x
        iters = 0
        phrase = ""

        while not i.nextkeywords == [] and not iters > 32:
            if phrase == "":
                phrase = i.thiskeyword
            else:
                phrase += " " + i.thiskeyword
            print phrase
            i = choice(i.nextkeywords)
            iters += 1

        return phrase
