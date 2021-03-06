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



import copy


# This class reads an exisiting S-Expression file (typical KiCad file)
# it builds up a tree with an Word object on each leaf
# each Word can be modified and then the whole tree can be saved to disk again
# The aim is to modify the file only on the positions, where needed,
# so a simple diff can show the changes.

class SExpressionModifier:
    # opens the file and reads all the lines into _content
    def __init__(self, fileName):
        self.fileName = fileName
        self._content = [] # contains all lines of the file
        self._tree = [] # list of Word objects and sublists

        try:
            file = open(fileName, mode='r', encoding='UTF8')

            nr = 0
            for line in file:
                self._content.append(line)
                nr += 1

            file.close()

            self.readTree()

        except Exception as e:
            print(e)


    # parses all the lines for '(module '
    #def extractFootprints(self):

    # parse s-expressions:
    def readTree(self):
        self._tree = [[]]
        path = [0] # list of integers, counting from 0, each entry corresponds to a level
        word = ''
        in_str = False
        lineNr = 0
        level = -1
        wordStart = 0
        wordIsQuoted = False
        for string in self._content:
            charNr = 0
            lastChar = ' ' # needed to detect escaped double quotes within a word
            for char in string:
                if char == '(' and not in_str:
                    self._tree.append([])
                    path.append(0)
                    level += 1
                elif char == ')' and not in_str:
                    if word:
                        self._tree[-1].append(Word(word, lineNr, wordStart, wordIsQuoted, level, path, self._tree[0]))
                        path[-1] += 1
                        word = ''
                    temp = self._tree.pop()
                    self._tree[-1].append(temp)
                    path.pop()
                    path[-1] += 1
                    level -= 1
                elif char in (' ', '\n', '\t') and not in_str:
                    if word:
                        self._tree[-1].append(Word(word, lineNr, wordStart, wordIsQuoted, level, path, self._tree[0]))
                        path[-1] += 1
                        word = ''
                elif char == '\"' and lastChar != '\\':
                    in_str = not in_str
                else:
                    if not word:
                        wordIsQuoted = in_str
                        wordStart = charNr
                    word += char

                charNr += 1
                lastChar = char
            # endf for each char
            lineNr += 1
        #end for each string

        self._tree = self._tree[0]

    def writeTree(self, fileName):
        # update content lines in reverse order
        # reverse order needed so the saved charNr for a word is correct.
        revIter = TreeIteratorReverse(self._tree, True)
        for w in revIter:
            lNr = w.lineNr
            oldLine = self._content[lNr]
            self._content[lNr] = w.updateLine(oldLine)

            if self._content[lNr] != oldLine:
                print('Info: modified line #' + str(lNr) + ': ' + self._content[lNr], end='')

        # write to file:
        try:
            file = open(fileName, mode='w', encoding='UTF8')
            file.writelines(self._content)
            file.close()
        except Exception as e:
            print(e)

    def printTree(self):
        treeIter = TreeIterator(self._tree, True)

        for word in treeIter:
            print(word)

    # prints a list of Word objects (recursively)
    def printBranch(self, root, indent):
        for e in root:
            if isinstance(e, list):
                self.printBranch(e, indent + 1)
            else:
                print(e)

    # returns a list of Word objects
    # word ... must match exactly
    # index ... number of path leaf (default = 0)
    def findWord(self, word, index):
        return findWord(self._tree, word, index, True)


class Word:
    def __init__(self, word, lineNr, charNr, quoted, level, path, root):
        self.word = word
        self.lineNr = lineNr # counting from 0
        self.charNr = charNr
        self.level = level
        self.path = copy.deepcopy(path)
        self.originalWord = ''
        self.quoted = quoted
        self.root = root

    def __str__(self):
        return self.path2str() + self.word + ' (L' + str(self.lineNr) + ' C' + str(self.charNr) + \
               ' TL' + str(self.level) + ')' # line char treelevel

    def path2str(self):
        s = '/'
        for i in self.path:
            s += str(i)
            s += '/'
        return s

    def modify(self, word: str):
        if word != self.word:
            if not self.originalWord:
                self.originalWord = self.word
            self.word = word

    def updateLine(self, line):
        if self.originalWord:
            part1 = line[0:self.charNr]
            part2 = str(line[self.charNr:])

            repl = self.word
            if not self.quoted and (' ' in self.word or '(' in self.word or ')' in self.word):
                repl = '\"' + repl + '\"'
            part2 = part2.replace(self.originalWord, repl, 1)
            line = part1 + part2

        return line


    # returs the list, which contains the given Word object
    def getParentList(self, levelsUp = 1):
        leaf = self.root
        path = copy.deepcopy(self.path)
        for i in range(levelsUp):
            path.pop()

        for i in path:
            leaf = leaf[i]

        return leaf

    # returns the word string next to a "Header Word Object" (index = 0)
    # returns None, if that would be a list, or self is not a "Header Word"
    def getValue(self):
        if self.path[-1] != 0:
            return None
        pl = self.getParentList()
        if not pl:  # parent list is empty
            return None
        if isinstance(pl[1], Word):
            return pl[1]
        else:
            return None

    def getValueStr(self):
        w = self.getValue()
        if w:
            return w.word
        else:
            return None


# returns a list of Word objects
# root ... list of Word objects and sublists
# word ... must match exactly
# index ... number of path leaf (default = 0)
# recursive ... search in sub and sub/sub lists too
def findWord(root: list, word: str, index: int, recursive: bool = False):
    resultList = []
    treeIter = TreeIterator(root, recursive)

    for wordObj in treeIter:
        if (treeIter.currentPath[-1] == index) and (wordObj.word == word):
            resultList.append(wordObj)

    return resultList

# Update a given tree dest with the values of the tree src
# both have to have the same structure
# src, dest ... list of Word objects and sublists
# TODO check for identical structure
def modifyTree(src: list, dest: list):
    srcIter = TreeIterator(src, True)
    destIter = TreeIterator(dest, True)

    for srcWord, destWord in zip(srcIter,destIter):
        if destWord.word != srcWord.word:
            print('  Info: modify: ' + destWord.word + ' -> ' + srcWord.word)
            destWord.modify(srcWord.word)



class TreeIterator:
    def __init__(self, root, recursive = False):
        self.currentPath = [-1] # list of integers
        self.currentPathLists = [] # stack of lists, for current path
        self.root = root
        self.recursive = recursive

    def __iter__(self):
        self.currentPath = [-1]
        self.currentPathLists = []
        self.currentPathLists.append(self.root)
        return self

    def __next__(self):
        candidate = []

        while isinstance(candidate, list):
            if self.currentPath[-1]+1 < len(self.currentPathLists[-1]):
                self.currentPath[-1] += 1
                candidate = self.currentPathLists[-1][self.currentPath[-1]]
                if isinstance(candidate, list) and self.recursive:
                    self.currentPath.append(-1)
                    self.currentPathLists.append(candidate)
            else: # we are at the end of the current sublist
                self.currentPath.pop()
                self.currentPathLists.pop()

                if not self.currentPathLists:
                    raise StopIteration

        return candidate

    def __str__(self):
        s = '/'
        for i in self.currentPath:
            s += str(i)
            s += '/'
        return s


class TreeIteratorReverse:
    def __init__(self, root, recursive = False):
        self.currentPath = [+1] # list of integers
        self.currentPathLists = [] # stack of lists, for current path
        self.root = root
        self.recursive = recursive

    def __iter__(self):
        self.currentPath = [+1]
        self.currentPathLists = []
        self.currentPathLists.append(self.root)
        return self

    def __next__(self):
        candidate = []

        while isinstance(candidate, list):
            if self.currentPath[-1]-1 >= 0:
                self.currentPath[-1] -= 1
                candidate = self.currentPathLists[-1][self.currentPath[-1]]
                if isinstance(candidate, list) and self.recursive:
                    self.currentPath.append(len(candidate)-1 +1)
                    self.currentPathLists.append(candidate)
            else: # we are at the end of the current sublist
                self.currentPath.pop()
                self.currentPathLists.pop()

                if not self.currentPathLists:
                    raise StopIteration

        return candidate

    def __str__(self):
        s = '/'
        for i in self.currentPath:
            s += str(i)
            s += '/'
        return s