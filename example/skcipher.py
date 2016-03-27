class NonAsciiMsgError(Exception):
    pass


class NotEnoughCharactersInKeyError(Exception):
    pass


def ciphermsg(msg, key):
    try:
        msg.decode('ascii')

    except UnicodeDecodeError:
        raise NonAsciiMsgError

    cipher_result = []
    for x in msg:

        try:
            cipher_result.append(key[ord(x)])

        except IndexError:
            raise NotEnoughCharactersInKeyError
    return "".join(cipher_result)
