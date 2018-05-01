

from SExpressionModifier import *

class Layout:
    def __init__(self, fileName):
        self.fileName = fileName
        self.sexp = SExpressionModifier(fileName)

    # returns a list of Word objects, which contain the relevant path to a 'module' in the file
    def getFootprints(self):
        l = []
        n = self.sexp.findWord('module', 0)
        for w in n:
            l.append(w.getValue())
        return l

    def write(self, fileName = ''):
        if not fileName:
            fileName = self.fileName
        self.sexp.writeTree(fileName)

    def update3dModel(self, srcModel: Word, destPcbModule: Word):
        srcModelTree = srcModel.getParentList()

        moduleTree = destPcbModule.getParentList()
        destModelTree = findWord(moduleTree, 'model', 0, True)[0].getParentList()

        modifyTree(srcModelTree, destModelTree)
