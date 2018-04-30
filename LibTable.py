

from SExpressionModifier import *

class LibTable:
    fileName = ''
    sexp = None

    def __init__(self, fileName):
        self.fileName = fileName
        self.sexp = SExpressionModifier(fileName)

    # returns a list of Word objects, which contain the relevant path to a 'name' in the file
    def getLibNames(self):
        return self.sexp.findWord('name', 0)

    # returns a Word object, which contains the URI
    def getUri(self, nameWordObj):
        lib = nameWordObj.getParentList()
        results = findWord(lib, 'uri', 0, True)
        return results[0].getValue()

    def write(self, fileName = fileName):
        self.sexp.writeTree(fileName)

