from hashlib import md5


def makeIdFromURI(uri):
    return md5(uri).hexdigest()
