

from SExpressionModifier import *

class LibTable:
    def __init__(self, fileName):
        self.fileName = fileName
        self.sexp = SExpressionModifier(fileName)

    # returns a list of Word objects, which contain the relevant path to a 'name' in the file
    def getLibNames(self):
        l = []
        n = self.sexp.findWord('name', 0)
        for w in n:
            l.append(w.getValue())
        return l

    def write(self, fileName = fileName):
        self.sexp.writeTree(fileName)


# returns a Word object, which contains the URI
def LibGetUri(nameWordObj):
    lib = nameWordObj.getParentList(2)
    results = findWord(lib, 'uri', 0, True)
    return results[0].getValue()