# crossword.py
# Dylan Steele + dylans + Section D

from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass
from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'c1491775ee5142754b00806ca92055078c19583aa60ea8c0c'
client = swagger.ApiClient(apiKey, apiUrl)

class CrosswordPuzzle(EventBasedAnimationClass):

    def __init__(self):
        blocksPerSide = 15
        height = 650
        widthOfBoard = 600
        widthOfHints = 400
        width = widthOfBoard + widthOfHints
        margin = 50
        blockWidth = (widthOfBoard - 2 * margin) / blocksPerSide
        super(CrosswordPuzzle, self).__init__(width, height)
        self.height = height
        self.widthOfBoard = widthOfBoard
        self.widthOfHints = widthOfHints
        self.width = width
        self.margin = margin
        self.blockWidth = blockWidth
        self.blocks = blocksPerSide        

    def initAnimation(self):
        self.wordApi = WordApi.WordApi(client)
        self.wordsApi = WordsApi.WordsApi(client)
        self.mode = None
        self.isMenuScreen = True
        self.isHelpScreen = False
        self.color = "White"
        self.selectedWordColor = "DodgerBlue2"
        self.selectedLetterColor = "Gold"
        self.selectedRow = None
        self.selectedCol = None
        self.direction = "across"
        self.initCreateMode()

    def onCreateButtonPressed(self):
        self.isMenuScreen = False
        self.mode = 0

    def onHelpButtonPressed(self):
        self.isMenuScreen = False
        self.isHelpScreen = True

    def onRightClick(self, event):
        if self.mode == 0 and self.isClickOnBoard(event):
            self.updateHints()
            row, col = self.getSelectedRowAndCol(event)
            if self.board[row][col] == None:
                self.board[row][col] = 1
                self.board[-row-1][-col-1] = 1
                if self.selectedRow == row:
                    self.selectedRow = None
                    self.selectedCol = None
            else:
                self.board[row][col] = None
                self.board[-row-1][-col-1] = None

    # find the row and column of the click
    def getSelectedRowAndCol(self, event):
        row = (event.y - self.margin*2)/self.blockWidth
        col = (event.x - self.margin)/self.blockWidth
        return row, col

    def onLeftClick(self, event):
        if self.isMenuScreen:
            self.onClickInMenu(event)
        elif self.isHelpScreen:
            pass
        elif self.mode == 0: #create mode
            if self.isClickOnBoard(event):
                self.titleEntry.config(state=DISABLED)
                row, col = self.getSelectedRowAndCol(event)
                if row == self.selectedRow and col == self.selectedCol:
                    self.switchDirections()
                else:
                    if self.board[row][col] != 1:
                        self.selectedRow, self.selectedCol = row, col
            if (event.widget == self.downHints or 
                event.widget == self.acrossHints):
                self.inCrosswordBoard = False
            elif event.widget == self.titleEntry:
                self.titleEntry.config(state=NORMAL)
                self.inCrosswordBoard = False
            else:
                self.inCrosswordBoard = True

    def isClickOnBoard(self, event):
        if (self.margin <= event.x <= self.blockWidth*self.blocks + 
                self.margin) and (self.margin*2 <= event.y <= self.blockWidth*
                self.blocks + self.margin*2) and event.widget == self.canvas:
            return True
        return False

    def switchDirections(self):
        if self.direction == "across":
            self.direction = "down"
        else:
            self.direction = "across"

    def onClickInMenu(self, event):
        # lots of magic numbers, will fix when menu screen style is finalyzed
        cx = self.width / 2
        if (cx - 80) <= event.x <= (cx + 80) and (200 <= event.y <= 280):
            self.isMenuScreen = False
            self.mode = 0
        elif (cx - 80) <= event.x <= (cx + 80) and (300 <= event.y <= 380):
            self.isMenuScreen = False
            self.mode = 1
        elif (cx - 80) <= event.x <= (cx + 80) and (400 <= event.y <= 480):
            self.isMenuScreen = False
            self.isHelpScreen = True

    def onKeyPressed(self, event):
        if self.mode == 0:
            if self.inCrosswordBoard and self.selectedRow != None:
                if event.keysym == "Tab":
                    self.goToNextWord()
                elif event.keysym == "BackSpace":
                    self.deleteLetter()
                elif event.keysym == "space":
                    self.goToNextLetter()
                elif event.keysym.isalpha() and len(event.keysym) == 1:
                    self.board[self.selectedRow][self.selectedCol] = \
                        event.keysym.upper()
                    self.goToNextLetter()
            elif event.widget == self.acrossHints:
                self.addHint(event, "across")
            elif event.widget == self.downHints:
                self.addHint(event, "down")

    def findPossibleWords(self):
        possibleWords = []
        currentWordIndexes = self.findCurrentWord()
        if currentWordIndexes == None:
            return possibleWords
        currentWord = ""
        for row, col in currentWordIndexes:
            letter = self.board[row][col]
            if letter == None:
                currentWord += "?"
            else:
                currentWord += letter
        currentWordLength = len(currentWord)
        words = self.wordsApi.searchWords(query=currentWord, 
                                          caseSensitive=False, 
                                          minLength=currentWordLength,
                                          maxLength=currentWordLength,
                                          limit=self.wordLimit)
        for i in xrange(len(words.searchResults)):
            possibleWords.append(words.searchResults[i].word)
        return possibleWords

    def findCurrentWord(self):
        if self.direction == "across":
            wordListToSearch = self.acrossWordList
        elif self.direction == "down":
            wordListToSearch = self.downWordList
        for word in wordListToSearch:
            if (self.selectedRow, self.selectedCol) in word:
                return word

    def deleteLetter(self):
        if self.direction == "down":
            self.board[self.selectedRow][self.selectedCol] = None
            if (self.board[self.selectedRow - 1][self.selectedCol] == 1 or
                self.selectedRow - 1 < 0):
                self.goToPreviousWord()
            else:
                self.selectedRow -= 1
        elif self.direction == "across":
            self.board[self.selectedRow][self.selectedCol] = None
            if (self.board[self.selectedRow][self.selectedCol - 1] == 1 or
                self.selectedCol - 1 < 0):
                self.goToPreviousWord()
            else:
                self.selectedCol -= 1

    def goToPreviousWord(self):
        letterIndex = (self.selectedRow, self.selectedCol)
        if self.direction == "down": 
            self.goToPreviousDownWord(letterIndex)
        elif self.direction == "across":
            self.goToPreviousAcrossWord(letterIndex)

    def goToPreviousDownWord(self, letterIndex):
        for wordIndex in xrange(len(self.downWordList)):
            for letter in self.downWordList[wordIndex]:
                if letter == letterIndex:
                    previousIndex = wordIndex - 1
                    if previousIndex >= 0:
                        previousWord = self.downWordList[previousIndex]
                        previousRow = previousWord[-1][0]
                        previousCol = previousWord[-1][1]
                        self.selectedRow = previousRow
                        self.selectedCol = previousCol
                    else:
                        self.switchDirections()
                        self.selectedRow = self.acrossWordList[-1][-1][0]
                        self.selectedCol = self.acrossWordList[-1][-1][1]

    def goToPreviousAcrossWord(self, letterIndex):
        for wordIndex in xrange(len(self.acrossWordList)):
            for letter in self.acrossWordList[wordIndex]:
                if letter == letterIndex:
                    previousIndex = wordIndex - 1
                    print previousIndex
                    if previousIndex >= 0:
                        previousWord = self.acrossWordList[previousIndex]
                        previousRow = previousWord[-1][0]
                        previousCol = previousWord[-1][1]
                        self.selectedRow = previousRow
                        self.selectedCol = previousCol
                    else:
                        self.switchDirections()
                        self.selectedRow = self.downWordList[-1][-1][0]
                        self.selectedCol = self.downWordList[-1][-1][1]

    def goToNextLetter(self):
        if self.direction == "down":
            if (self.selectedRow == (self.blocks - 1) or 
                self.board[self.selectedRow + 1][self.selectedCol] == 1):
                self.goToNextWord()
            else:
                self.selectedRow += 1
                while (self.selectedRow < self.blocks -1 and
                       self.board[self.selectedRow+1][self.selectedCol] !=None):
                    self.selectedRow += 1
        elif self.direction == "across":
            if (self.selectedCol == (self.blocks - 1) or
                self.board[self.selectedRow][self.selectedCol + 1] == 1):
                self.goToNextWord()
            else:
                self.selectedCol += 1
                while (self.selectedCol < self.blocks - 1 and
                       self.board[self.selectedRow][self.selectedCol+1] !=None):
                    self.selectedCol += 1

    def goToNextWord(self):
        letterIndex = (self.selectedRow, self.selectedCol)
        if self.direction == "down": 
            self.goToNextDownWord(letterIndex)
        elif self.direction == "across":
            self.goToNextAcrossWord(letterIndex)

    def goToNextDownWord(self, letterIndex):
        for wordIndex in xrange(len(self.downWordList)):
            for letter in self.downWordList[wordIndex]:
                if letter == letterIndex:
                    nextIndex = wordIndex + 1
                    if nextIndex < len(self.downWordList):
                        nextWord = self.downWordList[nextIndex]
                        nextRow = nextWord[0][0]
                        nextCol = nextWord[0][1]
                        self.selectedRow = nextRow
                        self.selectedCol = nextCol
                    else:
                        self.switchDirections()
                        self.selectedRow = self.acrossWordList[0][0][0]
                        self.selectedCol = self.acrossWordList[0][0][1]

    def goToNextAcrossWord(self, letterIndex):
        for wordIndex in xrange(len(self.acrossWordList)):
            for letter in self.acrossWordList[wordIndex]:
                if letter == letterIndex:
                    nextIndex = wordIndex + 1
                    if nextIndex < len(self.acrossWordList):
                        nextWord = self.acrossWordList[nextIndex]
                        nextRow = nextWord[0][0]
                        nextCol = nextWord[0][1]
                        self.selectedRow = nextRow
                        self.selectedCol = nextCol
                    else:
                        self.switchDirections()
                        self.selectedRow = self.downWordList[0][0][0]
                        self.selectedCol = self.downWordList[0][0][1]
        
    def redrawAll(self):
        self.canvas.delete(ALL)
        if self.isMenuScreen:
            self.drawMenuScreen()
        elif self.isHelpScreen:
            self.drawHelpScreen()
        elif self.mode == 0: #create mode
            self.drawCreateMode()

    def drawMenuScreen(self):
        # lots of magic numbers, will fix when menu screen style is finalyzed
        canvas = self.canvas
        cx = self.width / 2
        canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        canvas.create_text(cx, self.margin*2, text="Crosswordr",
                           font="Helvetica 48 bold")
        canvas.create_text(cx, self.margin*3, text="Dylan Steele",
                           font="Helvetica 28")
        canvas.create_rectangle(cx-80, 200, cx+80, 280, 
                                fill=self.selectedWordColor)
        canvas.create_text(cx, 240, text="Create", font="Helvetica 28 bold")
        canvas.create_rectangle(cx-80, 400, cx+80, 480, 
                                fill=self.selectedWordColor)
        canvas.create_text(cx, 440, text="Help", font="Helvetica 28 bold")

    def initCreateMode(self):
        self.wordLimit = 50
        self.board = [[None]*self.blocks for i in xrange(self.blocks)]
        self.wordColor = "black"
        self.errorColor = "red"
        self.colorOfLetters = [[self.wordColor]*self.blocks for i in 
                                xrange(self.blocks)]
        self.possibleWords = None
        self.showPossibleWords = True
        self.inCrosswordBoard = True
        self.wordList = self.findWords()
        self.numberList = self.findNumbers()
        self.numDirsList = self.findNumberDirections()
        self.initTitle()
        self.initWordSuggestions()
        self.initHints()
        self.updateHints()
        # sample board for testing purposes
        # self.board = [[None, None, None, None, None, None, None, 1, None, None, None, None, None, None, None],
        #               [None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None],
        #               [None, None, None, None, None, None, None, None, None, 1, None, None, None, None, None],
        #               [None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None],
        #               [1, None, None, None, None, None, None, 1, None, None, None, None, None, None, None],
        #               [None, 1, None, 1, None, 1, None, 1, 1, 1, None, 1, 1, 1, None],
        #               [None, None, None, None, 1, None, None, None, None, None, None, None, None, None, None],
        #               [None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None],
        #               [None, None, None, None, None, None, None, None, None, None, 1, None, None, None, None],
        #               [None, 1, 1, 1, None, 1, 1, 1, None, 1, None, 1, None, 1, None],
        #               [None, None, None, None, None, None, None, 1, None, None, None, None, None, None, 1],
        #               [None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None],
        #               [None, None, None, None, None, 1, None, None, None, None, None, None, None, None, None],
        #               [None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None, 1, None],
        #               [None, None, None, None, None, None, None, 1, None, None, None, None, None, None, None]]

    def findWords(self):
        self.acrossWordList = self.findWordsAcross()
        self.downWordList = self.findWordsDown()
        wordList = self.mergesort(self.acrossWordList + self.downWordList)
        return wordList

    def merge(self,A, B):
        if ((len(A) == 0) or (len(B) == 0)):
            return A+B
        else:
            if (A[0] < B[0]):
                return [A[0]] + self.merge(A[1:], B)
            else:
                return [B[0]] + self.merge(A, B[1:])

    def mergesort(self, L):        
        if (len(L) < 2):
            return L
        else:
            mid = len(L)/2
            left = self.mergesort(L[:mid])
            right = self.mergesort(L[mid:])
            return self.merge(left, right)

    def drawCreateMode(self):
        self.drawTitle()
        self.drawCrosswordBoard()
        if self.selectedRow != None:
            self.drawSelectedLetter()
            self.drawSelectedWord()
        self.drawWords()
        self.drawNumbers()
        if self.showPossibleWords:
            self.drawPossibleWords()
        else:
            self.drawHints()

    def initTitle(self):
        self.titleEntry = Entry(self.canvas, font="Helvetica 30 bold", 
                                justify=CENTER, highlightthickness=0,
                                disabledforeground="Gray")
        self.updateTitle()
        self.titleEntry.config(state=DISABLED)

    def updateTitle(self):
        if (self.titleEntry.cget('state') == 'disabled' and 
            len(self.titleEntry.get()) == 0):
            self.titleEntry.config(state=NORMAL)
            self.titleEntry.insert(0, "Title (click to change)")
            self.titleEntry.config(state=DISABLED)

    def drawTitle(self):
        canvas = self.canvas
        canvas.create_window(self.margin, self.margin, anchor=W, 
                             window=self.titleEntry, width=500)

    def drawHints(self):
        canvas = self.canvas
        canvas.create_text(self.widthOfBoard, 130, text="Across", 
                           font="Helvetica 24 bold", anchor=W)
        canvas.create_text(self.widthOfBoard, 380, text="Down",
                           font="Helvetica 24 bold", anchor=W)
        canvas.create_window(self.widthOfBoard, 145, anchor=NW, 
                             window=self.acrossFrame, width=350)
        canvas.create_window(self.widthOfBoard, 395, anchor=NW, 
                             window=self.downFrame, width=350)

    def initHints(self):
        self.acrossFrame = Frame(self.canvas)
        self.acrossScrollbar = Scrollbar(self.acrossFrame, orient=VERTICAL)
        self.acrossHints = Listbox(self.acrossFrame, font="Helvetica 16", 
                                   width=30, selectbackground="White",
                                   yscrollcommand=self.acrossScrollbar.set)
        self.acrossScrollbar.config(command=self.acrossHints.yview,)
        self.acrossScrollbar.pack(side=RIGHT, fill=Y)
        self.acrossHints.pack(side=LEFT, fill=BOTH, expand=1)        
        self.downFrame = Frame(self.canvas)
        self.downScrollbar = Scrollbar(self.downFrame, orient=VERTICAL)
        self.downHints = Listbox(self.downFrame, font="Helvetica 16", width=30,
                              yscrollcommand=self.downScrollbar.set,
                              selectbackground="White")
        self.downScrollbar.config(command=self.downHints.yview)
        self.downScrollbar.pack(side=RIGHT, fill=Y)
        self.downHints.pack(side=LEFT, fill=BOTH, expand=1)

    def addHint(self, event, direction):
        if direction == "across":
            hintDir = self.acrossHints
        elif direction == "down":
            hintDir = self.downHints
        hint = hintDir.get(ACTIVE)
        for i in xrange(hintDir.size()):
            if hintDir.get(i) == hint:
                indexToActivate = i
        hint = hint.split("\t")
        if event.keysym == "BackSpace":
            hint[1] = hint[1][:-1]
        elif event.keysym == "space":
            hint[1] += " "
        elif len(event.keysym) == 1:
            hint[1] += event.keysym
        hint = "\t".join(hint)
        hintDir.insert(ACTIVE, hint)
        hintDir.activate(indexToActivate)
        hintDir.delete(indexToActivate+1)

    def updateHints(self):
        self.acrossHints.delete(0, END)
        self.downHints.delete(0, END)
        for i in xrange(len(self.numDirsList)):
            text = "%s\t" % (self.numDirsList[i][0])
            if self.numDirsList[i][1] == "across":
                self.acrossHints.insert(END, text)
            elif self.numDirsList[i][1] == "down":
                self.downHints.insert(END, text)

    def initWordSuggestions(self):
        self.wordsFrame = Frame(self.canvas)
        self.wordsScrollbar = Scrollbar(self.wordsFrame, orient=VERTICAL)
        self.wordSuggestions = Listbox(self.wordsFrame, font="Helvetica 16", 
                                       width=30,
                                       yscrollcommand=self.wordsScrollbar.set,
                                       selectbackground="White",
                                       height=19)
        self.wordsScrollbar.config(command=self.wordSuggestions.yview)
        self.wordsScrollbar.pack(side=RIGHT, fill=Y)
        self.wordSuggestions.pack(side=LEFT, fill=BOTH, expand=1)

    def drawPossibleWords(self):
        canvas = self.canvas
        canvas.create_window(self.widthOfBoard, 135, anchor=NW, 
                             window=self.wordsFrame)
        canvas.create_text(self.widthOfBoard, 120, anchor=W, 
                           text="Word Suggestions", font="Helvetica 24 bold")
        canvas.create_rectangle(self.widthOfBoard, 540, 840, 595, 
                                fill=self.selectedWordColor)
        canvas.create_text(720, 568, text="Write Hints", 
                           font="Helvetica 24 bold")

    def drawCrosswordBoard(self):
        canvas = self.canvas
        for row in xrange(self.blocks):
            for col in xrange(self.blocks):
                top = self.margin*2 + row*self.blockWidth
                left = self.margin + col*self.blockWidth
                bottom = top + self.blockWidth
                right = left + self.blockWidth                
                color = self.color
                if self.board[row][col] == 1:
                    color = "black"
                canvas.create_rectangle(left, top, right, bottom, fill=color)

    def drawSelectedLetter(self):
        canvas = self.canvas
        top = self.margin*2 + self.selectedRow*self.blockWidth
        left = self.margin + self.selectedCol*self.blockWidth
        bottom = top + self.blockWidth
        right = left + self.blockWidth
        canvas.create_rectangle(left, top, right, bottom, 
                                fill=self.selectedLetterColor)

    def drawSelectedWord(self):
        if self.direction == "across":
            self.drawSelectedWordAcross()
        elif self.direction == "down":
            self.drawSelectedWordDown()
    
    def drawSelectedWordAcross(self):
        canvas = self.canvas
        for col in xrange(self.selectedCol + 1, self.blocks):
            if self.board[self.selectedRow][col] == 1:
                break
            top = self.margin*2 + self.selectedRow*self.blockWidth
            left = self.margin + col*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)
        for col in xrange(self.selectedCol - 1, -1, -1):
            if self.board[self.selectedRow][col] == 1:
                break
            top = self.margin*2 + self.selectedRow*self.blockWidth
            left = self.margin + col*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)

    def drawSelectedWordDown(self):
        canvas = self.canvas
        for row in xrange(self.selectedRow + 1, self.blocks):
            if self.board[row][self.selectedCol] == 1:
                break
            top = self.margin*2 + row*self.blockWidth
            left = self.margin + self.selectedCol*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)
        for row in xrange(self.selectedRow - 1, -1, -1):
            if self.board[row][self.selectedCol] == 1:
                break
            top = self.margin*2 + row*self.blockWidth
            left = self.margin + self.selectedCol*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)

    def drawWords(self):
        canvas = self.canvas
        for row in xrange(self.blocks):
            for col in xrange(self.blocks):
                x = self.margin + col*self.blockWidth + self.blockWidth/2
                y = self.margin*2 + row*self.blockWidth + self.blockWidth/2
                if self.board[row][col] != 1 and self.board[row][col] != None:
                    letter = self.board[row][col]
                    color = self.colorOfLetters[row][col]
                    canvas.create_text(x, y, text=letter, font="Helvetica 22",
                                       fill=color)

    def drawNumbers(self):
        canvas = self.canvas
        for i in xrange(len(self.numberList)):
            row, col = self.numberList[i]
            numberSpacing = 3
            x = self.margin + col*self.blockWidth + numberSpacing
            y = self.margin*2 + row*self.blockWidth
            canvas.create_text(x, y, text=i+1, font="Helvetica 12", 
                               anchor=NW)

    def onEvent(self):
        if self.mode == 0:
            self.updateTitle()
            self.wordList = self.findWords()
            self.numberList = self.findNumbers()
            self.checkWordsAreLegal()
            if self.showPossibleWords:
                self.possibleWords = self.findPossibleWords()
                self.updatePossibleWords()
            else:
                self.numDirsList = self.findNumberDirections()  

    def updatePossibleWords(self):
        self.wordSuggestions.delete(0, END)
        for word in self.possibleWords:
            self.wordSuggestions.insert(END, word)

    def checkWordsAreLegal(self):
        for wordIndexes in self.wordList:
            word = []
            for rowLetter, colLetter in wordIndexes:
                word.append(self.board[rowLetter][colLetter])
            if None not in word:
                word = "".join(word)
                word = word.lower()
                isWord = self.wordApi.getDefinitions(word)
                if isWord != None:
                    for row, col in wordIndexes:
                        self.colorOfLetters[row][col] = self.wordColor
                else:
                    for row, col in wordIndexes:
                        self.colorOfLetters[row][col] = self.errorColor

    def findWordsAcross(self, wordList=None, row=0, col=0):
        if wordList == None:
            wordList = []
        if row >= self.blocks:
            return wordList
        elif col > self.blocks - 1:
            return self.findWordsAcross(wordList, row+1, 0)
        elif self.board[row][col] == 1:
            return self.findWordsAcross(wordList, row, col+1)
        else:
            word = []
            for column in xrange(col, self.blocks):
                if self.board[row][column] == 1:
                    if len(word) > 1:
                        wordList.append(word)
                    return self.findWordsAcross(wordList, row, column+1)
                else:
                    word.append((row, column))
            if len(word) > 1:
                wordList.append(word)
            return self.findWordsAcross(wordList, row+1, 0)

    def findWordsDown(self, wordList=None, row=0, col=0):
        if wordList == None:
            wordList = []
        if col >= self.blocks:
            return wordList
        elif row > self.blocks - 1:
            return self.findWordsDown(wordList, 0, col+1)
        elif self.board[row][col] == 1:
            return self.findWordsDown(wordList, row+1, col)
        else:
            word = []
            for roww in xrange(row, self.blocks):
                if self.board[roww][col] == 1:
                    if len(word) > 1:
                        wordList.append(word)
                    return self.findWordsDown(wordList, roww+1, col)
                else:
                    word.append((roww, col))
            if len(word) > 1:
                wordList.append(word)
            return self.findWordsDown(wordList, 0, col+1)

    def findNumbers(self):
        numberList = []
        for i in xrange(len(self.wordList)):
            number = self.wordList[i][0]
            if number not in numberList:
                numberList.append(number)
        return numberList

    def findNumberDirections(self):
        numberAndDirection = []
        for i in xrange(len(self.numberList)):
            number = self.numberList[i]
            for j in xrange(len(self.acrossWordList)):
                numToCompare = self.acrossWordList[j][0]
                if numToCompare == number:
                    numberAndDirection.append((i+1, "across"))
            for j in xrange(len(self.downWordList)):
                numToCompare = self.downWordList[j][0]
                if numToCompare == number:
                    numberAndDirection.append((i+1, "down"))
        return numberAndDirection

CrosswordPuzzle().run()