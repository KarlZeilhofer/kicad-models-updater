# This file is part of kicad-models-updater
# Copyright (C) 2018 Karl Zeilhofer, www.team14.at
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




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



class Footprint:
    def __init__(self, wordObj: Word):
        self.pcbFP = wordObj # Word object to footprint in kicad_pcb
        ss = wordObj.word.split(':')
        if len(ss) != 2:
            print('Error: invalid or legacy footprint name: ' + wordObj.word + ' in line ' + str(wordObj.lineNr+1))
            exit()
        self.libName = ss[0] # e.g. standardSMD
        self.libFP = ss[1]  # e.g. R1608m
        self.footprintLibPath = ''

    def getFpId(self):
        return self.libName + ':' + self.libFP

    def __lt__(self, rhs):
        return self.getFpId() < rhs.getFpId()