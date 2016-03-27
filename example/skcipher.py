class NonAsciiMsgError(Exception):
    pass


class NotEnoughCharactersInKeyError(Exception):
    pass


def ciphermsg(msg, key):
    try:
        msg.decode('ascii')

    except UnicodeDecodeError:
        raise NonAsciiMsgError

    cipherresult = []
    for x in msg:

        try:
            cipherresult.append(key[ord(x)])

        except IndexError:
            raise NotEnoughCharactersInKeyError
    return "".join(cipherresult)
