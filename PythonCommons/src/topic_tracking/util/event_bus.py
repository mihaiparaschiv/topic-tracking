from collections import defaultdict


def EventBus(object):

    def __init__(self):
        self.__callbacks = defaultdict(list)

    def subscribe(self, type, callback):
        self.__callbacks[type].append(callback)

    def unsubcribe(self, type, callback):
        del self.__callbacks[type][callback]

    def emit(self, type, event):
        for callback in self.__callbacks:
            callback(event)


class Event(object):
    pass
