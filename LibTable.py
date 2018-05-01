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

    def write(self, fileName = ''):
        if not fileName:
            fileName = self.fileName
        self.sexp.writeTree(fileName)


# returns a Word object, which contains the URI
def LibGetUri(nameWordObj):
    lib = nameWordObj.getParentList(2)
    results = findWord(lib, 'uri', 0, True)
    return results[0].getValue()