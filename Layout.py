

from SExpressionModifier import *

class Layout:
    fileName = ''
    sexp = None

    def __init__(self, fileName):
        self.fileName = fileName
        self.sexp = SExpressionModifier(fileName)

    # returns a list of Word objects, which contain the relevant path to a 'module' in the file
    def getFootprints(self):
        return self.sexp.findWord('module', 0)

    def write(self, fileName = fileName):
        self.sexp.writeTree(fileName)

