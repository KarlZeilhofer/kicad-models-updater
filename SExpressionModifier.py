
import copy


# This class reads an exisiting S-Expression file (typical KiCad file)
# it builds up a tree with an Word object on each leaf
# each Word can be modified and then the whole tree can be saved to disk again
# The aim is to modify the file only on the positions, where needed,
# so a simple diff can show the changes.

class SExpressionModifier:


    _filename = ""
    _content = []
    _tree = [[]]

    footprints = [] # list of Footprint objects, found in the file


    # opens the file and reads all the lines into _content
    def __init__(self, fileName):
        self._filename = fileName

        try:
            file = open(fileName, mode='r', encoding='UTF8')

            nr = 0
            for line in file:
                self._content.append(line)
                nr += 1

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
            for char in string:
                if char is '(' and not in_str:
                    self._tree.append([])
                    path.append(0)
                    level += 1
                elif char is ')' and not in_str:
                    if word:
                        self._tree[-1].append(Word(word, lineNr, wordStart, wordIsQuoted, level, path, self._tree))
                        path[-1] += 1
                        word = ''
                    temp = self._tree.pop()
                    self._tree[-1].append(temp)
                    path.pop()
                    path[-1] += 1
                    level -= 1
                elif char in (' ', '\n', '\t') and not in_str:
                    if word:
                        self._tree[-1].append(Word(word, lineNr, wordStart, wordIsQuoted, level, path, self._tree))
                        path[-1] += 1
                        word = ''
                elif char is '\"':
                    in_str = not in_str
                else:
                    if not word:
                        wordIsQuoted = in_str
                        wordStart = charNr
                    word += char

                charNr += 1
            # endf for each char
            lineNr += 1
        #end for each string

        self._tree = self._tree[0]

    def writeTree(self, fileName):
        # TODO
        # die listen müssen rückwärts durchlaufen werden, sodass der index Word::charNr gültig ist.
        # und somit die jeweiligen zeilen aktualisiert werden.
        # dann können alle zeilen in die datei geschrieben werden.
        print("TODO: wirteTree()")

    def printTree(self):
        treeIter = TreeIterator(self._tree, True)

        for word in treeIter:
            print(word)
            print(treeIter)

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
    word = ""
    lineNr = 0
    charNr = 0
    level = 0
    path = []
    originalWord = '' # if not empty, this word has been modified
    quoted = False
    root = None


    def __init__(self, word, lineNr, charNr, quoted, level, path, root):
        self.word = word
        self.lineNr = lineNr
        self.charNr = charNr
        self.level = level
        self.path = copy.deepcopy(path)
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

    def setWord(self, word):
        if word is not self.word:
            if not self.originalWord:
                self.originalWord = self.word
            self.word = word

    def updateLine(self, line):
        if self.originalWord:
            part1 = line[0:self.charNr]
            part2 = str(line[self.charNr:])

            repl = self.word
            if not self.quoted and self.word.count(' ') > 0:
                repl = '\"' + repl + '\"'
            part2.replace(self.originalWord, repl, 1)
            return part1+part2

        return line


    # returs the list, which contains the given Word object
    def getParentList(self):
        leaf = self.root
        path = self.path
        path.pop()

        for i in path:
            leaf = leaf[i]

        return leaf

    # returns the word string next to a "Header Word Object" (index = 0)
    # returns None, if that would be a list, or self is not a "Header Word"
    def getValue(self):
        if self.path[-1] is not 0:
            return None
        if not self.getParentList(): # parent list is empty
            return None
        if isinstance(self.getParentList()[1], Word):
            return self.getParentList()[1].word
        else:
            return None


# returns a list of Word objects
# root ... list of Word objects and sublists
# word ... must match exactly
# index ... number of path leaf (default = 0)
# recursive ... search in sub and sub/sub lists too
def findWord(root, word, index, recursive = False):
    resultList = []
    treeIter = TreeIterator(root, recursive)

    for wordObj in treeIter:
        if treeIter.currentPath[-1] == index and wordObj.word == word:
            resultList.append(wordObj)

    return resultList


class TreeIterator:
    currentPath = [-1] # list of integers
    currentPathLists = [] # stack of lists, for current path
    root = None
    recursive = False

    def __init__(self, root, recursive = False):
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