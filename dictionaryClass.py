# dictionaryClass.py
# Dylan Steele + dylans + Section D

class Dictionary(object):
    def __init__(self):
        self.filename = "dictionary.txt"
        self.dictionary = self.createWordDictionary()

    def createWordDictionary(self):
        dictionaryText = Dictionary.readFile(self.filename)
        wordDictionary = dict()
        for word in dictionaryText.splitlines():
            wordDictionary[word.upper()] = len(word)
        return wordDictionary

    @staticmethod
    def readFile(filename, mode="rt"):
        with open(filename, mode) as fin:
            return fin.read()