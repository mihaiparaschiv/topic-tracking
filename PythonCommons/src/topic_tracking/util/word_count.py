class WordCountProvider(object):
    
    def __init__(self):
        self.__table = dict()
    
    def set(self, word, pos, count):
        self.__table[(word, pos)] = count
    
    def get(self, word, pos):
        return self.__table.get((word, pos), None)