# crosswordCreator.py
# Dylan Steele + dylans + Section D

# import copy to create a copy of the board
# import urllib2 to check for internet connection
# import tkMessageBox to create an error message
# import wordnik for word searches (https://github.com/wordnik/wordnik-python)
import copy, urllib2, tkMessageBox
from wordnik import *
from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass

# wordnik api configuration
apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'c1491775ee5142754b00806ca92055078c19583aa60ea8c0c'
client = swagger.ApiClient(apiKey, apiUrl)

class CrosswordCreator(EventBasedAnimationClass):

    # initalizes the main properties of CrosswordCreator canvas
    def __init__(self):
        # number of blocks per side (15x15 grid for the crossword)
        blocksPerSide = 15
        # static canvas size (height and width)
        height = 650
        widthOfBoard = 600
        widthOfHints = 400
        width = widthOfBoard + widthOfHints
        margin = 50
        blockWidth = (widthOfBoard - 2 * margin) / blocksPerSide
        # init with the superclass (EventBasedAnimationClass)
        super(CrosswordCreator, self).__init__(width, height)
        self.height = height
        self.widthOfBoard = widthOfBoard
        self.widthOfHints = widthOfHints
        self.width = width
        self.margin = margin
        self.blockWidth = blockWidth
        self.blocks = blocksPerSide        

    # initalize the main game variable states
    def initAnimation(self):
        # create Api objects for the word and words wordnik API
        self.wordApi = WordApi.WordApi(client)
        self.wordsApi = WordsApi.WordsApi(client)
        # does not start off in create mode
        self.mode = None
        # starts in menu screen
        self.isMenuScreen = True
        self.isHelpScreen = False
        # define main color scheme
        self.color = "White"
        self.selectedWordColor = "DodgerBlue2"
        self.selectedLetterColor = "Gold"
        # no selected row and column to begin
        self.selectedRow = None
        self.selectedCol = None
        # start with the selection going across (horizontally)
        self.direction = "across"
        # initalize the other parts of the game
        self.initMenuScreen()
        self.initCreateMode()
        self.initHelpScreen()

    # when the new puzzle button is clicked, checks for internet connection
    # if it has one, then it proceeds to the create mode
    # else, it notifies the user to connect to the internet
    def onCreateButtonPressed(self):
        if self.checkInternetConnection():
            self.isMenuScreen = False
            self.mode = 0
        else:
            self.raiseInternetError()

    # error message to display if there is no internet
    # taken from classnotes on Tkinter message box
    def raiseInternetError(self):
        message = "Please connect to the Internet."
        title = "Error"
        tkMessageBox.showerror(title, message)

    # checks if there is an internet connection
    # http://stackoverflow.com/questions/3764291/checking-network-connection
    def checkInternetConnection(self):
        try:
            response=urllib2.urlopen('http://74.125.228.100',timeout=1)
            return True
        except urllib2.URLError as err: pass
        return False

    # changes the view from the menu screen to the help screen
    def onHelpButtonPressed(self):
        self.isMenuScreen = False
        self.isHelpScreen = True

    # changes the view to the menu screen from the help screen or create mode
    def onBackToMenuButton(self):
        self.isMenuScreen = True
        self.isHelpScreen = False
        self.mode = None
        # restart initialize the element states (for a new game)
        self.initAnimation()

    # if there is a click in the menu screen, find if it was on a button
    def onClickInMenu(self, event):
        # new puzzle button
        if ((self.newGameX1 <= event.x <= self.newGameX2) and (self.newGameY1 <=
            event.y <= self.newGameY2)):
            self.onCreateButtonPressed()
        # help screen button
        elif ((self.helpX1 <= event.x <= self.helpX2) and (self.helpY1 <=
              event.y <= self.helpY2)):
            self.onHelpButtonPressed()

    # initialize the coordinates of the menu screen objects
    def initMenuScreen(self):
        self.cx = self.width / 2
        # all menu screen buttons should have the same height and width
        self.buttonWidth = 240
        self.buttonHeight = 80
        self.titleY = 125
        # new game button
        self.newGameX1 = self.cx - self.buttonWidth / 2
        self.newGameX2 = self.cx + self.buttonWidth / 2
        self.newGameY1 = 280
        self.newGameY2 = self.newGameY1 + self.buttonHeight
        # help screen button
        self.helpX1 = self.newGameX1
        self.helpX2 = self.newGameX2
        self.helpY1 = 400
        self.helpY2 = self.helpY1 + self.buttonHeight

    # initialize the coordinates of the help screen objects
    def initHelpScreen(self):
        # load the instructions from the instructions file
        self.instructionsFile = "instructions.txt"
        self.instructions = self.readFile(self.instructionsFile)
        # coordinates of the title, instructions, and main menu button
        self.instructionX = 100
        self.instructionY = 80
        self.borderHeight = 50
        self.mainMenuMargin = 10
        self.mainMenuWidth = 200

    # handles right click events
    def onRightClick(self, event):
        # only do something if creating a crossword and event is on board
        if self.mode == 0 and self.isClickOnBoard(event):
            row, col = self.getSelectedRowAndCol(event)
            # if the current row and column is white, set it to black (1)
            # and set the radially symmetric row and column to black too
            if self.board[row][col] == None:
                self.board[row][col] = 1
                self.board[-row-1][-col-1] = 1
                # if the selected cell was just turned black, unselect it
                if self.selectedRow == row:
                    self.selectedRow = None
                    self.selectedCol = None
            # if the current row and column is black, set it to white (None)
            # and set the radially symmetric row and column to white too
            else:
                self.board[row][col] = None
                self.board[-row-1][-col-1] = None

    # find the row and column of the click
    def getSelectedRowAndCol(self, event):
        row = (event.y - self.margin*2)/self.blockWidth
        col = (event.x - self.margin)/self.blockWidth
        return row, col

    # handles left click events
    def onLeftClick(self, event):
        # each screen has their own actions for left clicks
        if self.isMenuScreen:
            self.onClickInMenu(event)
        elif self.isHelpScreen:
            self.onClickinHelpScreen(event)
        # creating a crossword
        elif self.mode == 0: 
            # only react to board clicks if the user is not entering in hints
            if self.isClickOnBoard(event) and self.showPossibleWords:
                # now in the crossword board
                self.inCrosswordBoard = True
                # turn off word suggestions
                self.suggestWords = False
                # reset possibleWords to blank
                self.possibleWords = []
                self.updatePossibleWords()
                # unselect the titleEntry widget (disable it for now)
                self.titleEntry.config(state=DISABLED)
                row, col = self.getSelectedRowAndCol(event)
                # if the click is in the selected box, switch directions
                if row == self.selectedRow and col == self.selectedCol:
                    self.switchDirections()
                else:
                    # only select where the user clicked if it is not black
                    if self.board[row][col] != 1:
                        self.selectedRow, self.selectedCol = row, col
            else:
                # handles non-board clicks
                self.clickNotOnBoard(event)

    def onClickinHelpScreen(self, event):
        # if click is in the menu button
        if ((0 <= event.x <= self.mainMenuWidth) and 
            (0 <= event.y <= self.borderHeight)):
            self.onBackToMenuButton()

    # handles non-board clicks while creating crossword
    def clickNotOnBoard(self, event):
        # if click was in the hints widget, no longer in the board
        if (event.widget == self.downHints or 
            event.widget == self.acrossHints):
            self.inCrosswordBoard = False
        # if the click was in the title widget, no longer in the board,
        # and the title can now be edited by the user
        elif event.widget == self.titleEntry:
            self.inCrosswordBoard = False
            self.titleEntry.config(state=NORMAL)
        # if the click was in the word suggestions widget and there is a
        # selected word, insert the word in the selected word
        elif event.widget == self.wordSuggestions and self.selectedRow != None:
            self.insertSelectedWord(event)
        # go to hints screen if all done with board
        elif self.isClickOnNextButton(event):
            self.enterHints()
        elif self.isClickOnSaveButtonWithSolution(event):
            self.save(True)
        elif self.isClickOnSaveButtinWithoutSolution(event):
            self.save(False)
        elif self.isMainMenuClick(event):
            self.onBackToMenuButton()
        else:
            # if not in a widget, you are in board
            self.inCrosswordBoard = True

    # checks if a click is in the main menu button in create mode
    def isMainMenuClick(self, event):
        if ((self.mainMenuX1 <= event.x <= self.mainMenuX2) and
            (self.mainMenuY1 <= event.y <= self.mainMenuY2)):
            return True
        return False

    # checks if a click is in the save with solution button
    def isClickOnSaveButtonWithSolution(self, event):
        if ((600 <= event.x <= 762) and (540 <= event.y <= 595) and not
            self.showPossibleWords):
            return True
        return False

    # checks if a click is in the save without solution button
    def isClickOnSaveButtinWithoutSolution(self, event):
        if ((772 <= event.x <= 935) and (540 <= event.y <= 595) and not
            self.showPossibleWords):
            return True
        return False

    # taken from class notes for writing a file
    def writeFile(self, filename, contents, mode="wt"):
        # wt = "write text"
        with open(filename, mode) as fout:
            fout.write(contents)

    # saves the current game state with our without solution
    def save(self, withSolution):
        # file name will be the title of the puzzle ('with-solution' appended
        # if the file will have the soluton)
        fileName = self.getTitle()
        if withSolution:
            fileName += "-with-solution"
        fileName += ".txt"
        # get the contents for the file
        contents = self.getContents(withSolution)
        self.writeFile(fileName, contents)

    # returns the current puzzle state (title, board, and hints)
    # board state depends on if withSolution
    def getContents(self, withSolution):
        contents = ""
        title = self.getTitle()
        board = self.getBoard(withSolution)
        hints = self.getHints()
        contents += title + "\n\n"
        contents += board + "\n\n"
        contents += hints
        return contents

    # returns the text of the titleEntry widget
    def getTitle(self):
        return self.titleEntry.get()

    # returns a formated 2d list of the board
    def getBoard(self, withSolution):
        # create a copy of the board
        board = copy.deepcopy(self.board)
        for row in xrange(len(board)):
            for col in xrange(len(board[row])):
                # if cell is blank, do not place anything inside brackets
                if board[row][col] == None:
                    board[row][col] = "[ ]"
                # if cell is black, block it off
                elif board[row][col] == 1:
                    board[row][col] = "[*]"
                # if cell has a letter but withSolution is False, do not place
                # anything inside brackets
                elif board[row][col].isalpha() and not withSolution:
                    board[row][col] = "[ ]"
                # place the letter inside the brackets if withSoltion is True
                elif board[row][col].isalpha() and withSolution:
                    board[row][col] = "[%s]" % (board[row][col].upper())
        # format the board
        board = self.print2dList(board)
        return board

    # taken from class notes and modified to return the result instead of
    # printing it
    def print2dList(self, a):
        result = ""
        if (a == []):
            # So we don't crash accessing a[0]
            return
        rows = len(a)
        cols = len(a[0])
        # only single letter, plus space, so fieldWidth is 2
        fieldWidth = 2
        for row in xrange(rows):
            if (row > 0): result += "\n"
            for col in xrange(cols):
                format = "%" + str(fieldWidth) + "s"
                result += format % str(a[row][col])
        return result

    # returns a string of the hints
    def getHints(self):
        hints = ""
        # for both list of hints
        for listOfHints in [self.acrossHints, self.downHints]:
            # add the title of the hints
            if listOfHints == self.acrossHints:
                # no new line above since Across is first one to show
                hints += "Across\n"
            else:
                # Down is second, so it needs spacing
                hints += "\nDown\n"
            # get all of the hints for each direction
            dirHints = listOfHints.get(0, END)
            for dirHint in dirHints:
                # add each hint to the hints string with its own line
                hints += dirHint + "\n"
        return hints

    # sets game state to being able to enter in hints
    # finds the numbers of words associated with each direction
    # and updates the hints with those numbers to start
    def enterHints(self): 
        if self.showPossibleWords:
            self.showPossibleWords = False
            # deselect cell if one is currently selected
            self.selectedRow = self.selectedCol = None
            self.numDirsList = self.findNumberDirections()
            self.updateHints()        

    # checks if click is within the button for the next mode
    def isClickOnNextButton(self, event):
        if ((self.widthOfBoard <= event.x <= 840) and (540 <= event.y <= 595)
            and self.showPossibleWords):
            return True
        return False

    # inserts the selectedword in the suggested word list into the board
    def insertSelectedWord(self, event):
        coordinates = "@%d,%d" % (event.x, event.y)
        # find the word closest to the coordinates
        selectedWord = self.wordSuggestions.get(coordinates)
        # find the current word and its indexes
        currentWordIndexes = self.findCurrentWordIndexes()
        # place the selected word letter by letter into the selected word
        for i in xrange(len(currentWordIndexes)):
            row = currentWordIndexes[i][0]
            col = currentWordIndexes[i][1]
            self.board[row][col] = selectedWord[i].upper()

    # checks if a click is withint the actual crossword board
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

    # handles key press events
    def onKeyPressed(self, event):
        # only respond if creating a crossword
        if self.mode == 0:
            # if you are in the crossword board
            if self.inCrosswordBoard and self.selectedRow != None:
                if event.keysym in ["Left", "Right", "Up", "Down"]:
                    self.directionChange(event.keysym)
                if event.keysym == "Tab":
                    self.goToNextWord()
                elif event.keysym == "BackSpace":
                    self.deleteLetter()
                elif event.keysym == "space":
                    self.goToNextLetter()
                elif event.keysym == "Escape":
                    # find possible words with escape button
                    if self.suggestWords:
                        self.suggestWords = False
                        self.possibleWords = []
                        self.updatePossibleWords()
                    # disable find possible words if currently finding
                    else:
                        self.suggestWords = True
                # set the current cell to the letter and advance a letter
                elif event.keysym.isalpha() and len(event.keysym) == 1:
                    self.board[self.selectedRow][self.selectedCol] = \
                        event.keysym
                    self.goToNextLetter()
            # if click was in hints widget, add it
            elif event.widget == self.acrossHints:
                self.addHint(event, "across")
            elif event.widget == self.downHints:
                self.addHint(event, "down")

    # changes direction of the selection with a key press
    def directionChange(self, direction):
        if direction == "Left":
            # go back a column until you reach a white space
            self.selectedCol -= 1
            while (self.selectedCol >= 0 and
                   self.board[self.selectedRow][self.selectedCol] != None):
                self.selectedCol -= 1
        elif direction == "Right":
            # go forward a column until you reach a white space
            self.selectedCol += 1
            while (self.selectedCol < self.blocks - 1 and
                   self.board[self.selectedRow][self.selectedCol] != None):
                self.selectedCol += 1
        elif direction == "Up":
            # go up a row until you reach a white space
            self.selectedRow -= 1
            while (self.selectedRow >= 0 and
                   self.board[self.selectedRow][self.selectedCol] != None):
                self.selectedRow -= 1
        else:
            # go down a row until you reach a white space
            self.selectedRow += 1
            while (self.selectedRow < self.blocks - 1 and
                   self.board[self.selectedRow][self.selectedCol] != None):
                self.selectedRow += 1

    # returns a list of possible words for the selected word
    def findPossibleWords(self):
        possibleWords = []
        curWordIndexes = self.findCurrentWordIndexes()
        connectingWords = self.findConnectingWords(curWordIndexes)
        # return an empty list right away if no word is selected
        if curWordIndexes == None:
            return possibleWords
        # creates a string of the current word
        curWord = self.createCurrentWord(curWordIndexes)
        curWordLength = len(curWord)
        # wordnik query for the curWord of that length
        # only find a certain number of words (to decrease lag)
        words = self.wordsApi.searchWords(query=curWord, limit=self.wordLimit,
                                          caseSensitive=False, 
                                          maxLength=curWordLength,
                                          minLength=1)
        # for each word, find if it can be placed on the board legally
        for i in xrange(len(words.searchResults)):
            wordToCheck = words.searchResults[i].word
            if self.isLegalWord(wordToCheck, connectingWords):
                possibleWords.append(wordToCheck)
        if len(words.searchResults) == 0:
            possibleWords = []
        return possibleWords

    # checks if a word can be legally placed onto the crossword board
    def isLegalWord(self, word, connectingWords):
        # cannot use compound words or multiple words in one word
        if "-" in word or " " in word:
            return False
        # if connecteWords is None, then word will for sure fit (only based
        # on length)
        if connectingWords != None:
            # check if word works for each of the connecting words
            for connectingWord in connectingWords:
                connectingWordStr = self.createCurrentWord(connectingWord[0])
                curIndex = connectingWord[1]
                connectingIndex = connectingWord[2]
                connectingWordStr = (connectingWordStr[:connectingIndex] +
                                    word[curIndex] +
                                    connectingWordStr[connectingIndex+1:])
                maxLength = len(connectingWordStr)
                # make sure that the newly formed word is an actual word
                # (or can be an actual word if there are wildcards)
                temp = self.wordsApi.searchWords(query=connectingWordStr, 
                                                 limit=1, caseSensitive=False, 
                                                 maxLength=maxLength,
                                                 minLength=1)
                # if the word is not a real word, return False
                if len(temp.searchResults) == 0:
                    return False
        return True

    # formats the current word for wordnik query and returns the string of the
    # formatted word
    def createCurrentWord(self, currentWordIndexes):
        currentWord = ""
        # iterate through each cell/letter of the current word
        for row, col in currentWordIndexes:
            letter = self.board[row][col]
            if letter == None:
                # add wildcard if there is no letter in the cell
                currentWord += "?"
            else:
                # add the letter if there is one
                currentWord += letter
        return currentWord

    # returns the word that the selected cell is in
    def findCurrentWordIndexes(self):
        if self.direction == "across":
            wordListToSearch = self.acrossWordList
        elif self.direction == "down":
            wordListToSearch = self.downWordList
        for word in wordListToSearch:
            if (self.selectedRow, self.selectedCol) in word:
                return word

    # returns a list of connected words to the current word indexes
    def findConnectingWords(self, curWordIndexes):
        connectingWords = []
        # if there is no curWordIndexes, there will be no connecting words
        if curWordIndexes == None:
            return None
        # search the opposite list of words to find intersections
        if self.direction == "across":
            wordListToSearch = self.downWordList
        elif self.direction == "down":
            wordListToSearch = self.acrossWordList
        for word in wordListToSearch:
            for curWordIndex in curWordIndexes:
                if curWordIndex in word:
                    connectingIndex = word.index(curWordIndex)
                    curIndex = curWordIndexes.index(curWordIndex)
                    connectingWords.append((word, curIndex, connectingIndex))
        return connectingWords

    # deletes the current selected letter and moves back a space
    def deleteLetter(self):
        if self.direction == "down":
            # set the current cell to None (blank)
            self.board[self.selectedRow][self.selectedCol] = None
            # do not move back if the previous cell is black or the first letter
            if (self.board[self.selectedRow - 1][self.selectedCol] == 1 or
                self.selectedRow - 1 < 0):
                return
            # otherwise, move back
            else:
                self.selectedRow -= 1
        elif self.direction == "across":
            # set the current cell to None (blank)
            self.board[self.selectedRow][self.selectedCol] = None
            # do not move back if the previous cell is black or the first letter
            if (self.board[self.selectedRow][self.selectedCol - 1] == 1 or
                self.selectedCol - 1 < 0):
                return
            # otherwise, move back
            else:
                self.selectedCol -= 1

    def goToPreviousWord(self):
        letterIndex = (self.selectedRow, self.selectedCol)
        if self.direction == "down": 
            self.goToPreviousDownWord(letterIndex)
        elif self.direction == "across":
            self.goToPreviousAcrossWord(letterIndex)

    # find the current word and then find the previous word
    # set the selected cell to the first letter in the previous word
    def goToPreviousDownWord(self, letterIndex):
        for wordIndex in xrange(len(self.downWordList)):
            for letter in self.downWordList[wordIndex]:
                # find the current word
                if letter == letterIndex:
                    previousIndex = wordIndex - 1
                    if previousIndex >= 0:
                        previousWord = self.downWordList[previousIndex]
                        previousRow = previousWord[-1][0]
                        previousCol = previousWord[-1][1]
                        self.selectedRow = previousRow
                        self.selectedCol = previousCol
                    # if at the beginning of the down list, go to the end of the
                    # across list
                    else:
                        self.switchDirections()
                        self.selectedRow = self.acrossWordList[-1][-1][0]
                        self.selectedCol = self.acrossWordList[-1][-1][1]

    def goToPreviousAcrossWord(self, letterIndex):
        for wordIndex in xrange(len(self.acrossWordList)):
            for letter in self.acrossWordList[wordIndex]:
                if letter == letterIndex:
                    previousIndex = wordIndex - 1
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

    # advances the selected letter to the next blank space (or word)
    def goToNextLetter(self):
        if self.direction == "down":
            # if the next spot is black or the end of the column, go to the 
            # next word
            if (self.selectedRow == (self.blocks - 1) or 
                self.board[self.selectedRow][self.selectedCol] == 1):
                self.goToNextWord()
            # otherwise, go the the next blank space
            else:
                self.selectedRow += 1
                while (self.selectedRow < self.blocks - 1 and
                       self.board[self.selectedRow][self.selectedCol] != None):
                    self.selectedRow += 1
        elif self.direction == "across":
            # if the next spot is black or the end of the row, go to the 
            # next word
            if (self.selectedCol == (self.blocks - 1) or
                self.board[self.selectedRow][self.selectedCol] == 1):
                self.goToNextWord()
            # otherwise, go the the next blank space
            else:
                self.selectedCol += 1
                while (self.selectedCol < self.blocks - 1 and
                       self.board[self.selectedRow][self.selectedCol] != None):
                    self.selectedCol += 1

    # advances the selected cell to the start of the next word
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
        
    # redraws the canvas depending on which screen/mode
    def redrawAll(self):
        self.canvas.delete(ALL)
        if self.isMenuScreen:
            self.drawMenuScreen()
        elif self.isHelpScreen:
            self.drawHelpScreen()
        elif self.mode == 0:
            self.drawCreateMode()

    # draws the main menu screen
    def drawMenuScreen(self):
        canvas = self.canvas
        # title
        canvas.create_text(self.cx, self.titleY, text="Crossword Creator",
                           font="Helvetica 64 bold")
        # new game button shape
        canvas.create_rectangle(self.newGameX1, self.newGameY1, self.newGameX2,
                                self.newGameY2, fill=self.selectedWordColor)
        # new game text
        canvas.create_text(self.cx, (self.newGameY2+self.newGameY1)/2, 
                           text="New Crossword", font="Helvetica 28 bold")
        # help button shape
        canvas.create_rectangle(self.helpX1, self.helpY1, self.helpX2, 
                                self.helpY2, fill=self.selectedWordColor)
        # help button text
        canvas.create_text(self.cx, (self.helpY2+self.helpY1)/2, text="Help", 
                           font="Helvetica 28 bold")

    # initializes the variables for the create mode
    def initCreateMode(self):
        # number of word suggestions
        self.wordLimit = 6
        self.board = [[None]*self.blocks for i in xrange(self.blocks)]
        # location of main menu button
        self.mainMenuX1 = 800
        self.mainMenuX2 = 985
        self.mainMenuY1 = 20
        self.mainMenuY2 = 80
        # colors of letters on board
        self.wordColor = "black"
        self.errorColor = "red"
        self.colorOfLetters = [[self.wordColor]*self.blocks for i in 
                                xrange(self.blocks)]
        # game state starts showing the possible word screen without suggesting
        # any word and focused on the crossword board
        self.possibleWords = None
        self.showPossibleWords = True
        self.suggestWords = False
        self.inCrosswordBoard = True
        # find the words and numbers of the initial board
        self.wordList = self.findWords()
        self.numberList = self.findNumbers()
        # initalize the other aspects of the create mode
        self.initTitle()
        self.initWordSuggestions()
        self.initHints()

    # returns combined word list of the differnt words going down and across
    def findWords(self):
        self.acrossWordList = self.findWordsAcross()
        self.downWordList = self.findWordsDown()
        # sorted by the row (first elem in coordinate tuple)
        # use mergesort to merge the two lists together
        wordList = self.mergesort(self.acrossWordList + self.downWordList)
        return wordList

    # taken from class notes
    def merge(self,A, B):
        if ((len(A) == 0) or (len(B) == 0)):
            return A+B
        else:
            if (A[0] < B[0]):
                return [A[0]] + self.merge(A[1:], B)
            else:
                return [B[0]] + self.merge(A, B[1:])

    # taken from class notes
    def mergesort(self, L):        
        if (len(L) < 2):
            return L
        else:
            mid = len(L)/2
            left = self.mergesort(L[:mid])
            right = self.mergesort(L[mid:])
            return self.merge(left, right)

    # draws the create mode screen
    def drawCreateMode(self):
        self.drawTitle()
        self.drawCrosswordBoard()
        if self.selectedRow != None:
            self.drawSelectedLetter()
            self.drawSelectedWord()
        self.drawWords()
        self.drawNumbers()
        self.drawMenuButton()
        if self.showPossibleWords:
            self.drawPossibleWords()
        else:
            self.drawHints()
            self.drawSaveButtons()

    # draws the menu button when in create mode
    def drawMenuButton(self):
        canvas = self.canvas 
        # menu button shape
        canvas.create_rectangle(self.mainMenuX1, self.mainMenuY1, 
                                self.mainMenuX2, self.mainMenuY2,
                                fill=self.selectedWordColor)
        # menu button text
        canvas.create_text((self.mainMenuX2+self.mainMenuX1)/2, 
                            (self.mainMenuY1+self.mainMenuY2)/2, 
                            text="Main Menu", font="Helvetica 24 bold")

    # initialize the titleEntry widget and its text
    def initTitle(self):
        self.titleEntry = Entry(self.canvas, font="Helvetica 30 bold", 
                                justify=CENTER, highlightthickness=0,
                                disabledforeground="Gray")
        self.updateTitle()
        self.titleEntry.config(state=DISABLED)

    # updates the title
    def updateTitle(self):
        # if the title is in the disabled state and it is blank (len of 0)
        if (self.titleEntry.cget('state') == 'disabled' and 
            len(self.titleEntry.get()) == 0):
            # set it to normal so it can be modified
            self.titleEntry.config(state=NORMAL)
            # change the title to the placeholder text
            self.titleEntry.insert(0, "Title (click to change)")
            # set it back to disabled mode
            self.titleEntry.config(state=DISABLED)

    # draws the title during create mode
    def drawTitle(self):
        canvas = self.canvas
        canvas.create_window(self.margin, self.margin, anchor=W, 
                             window=self.titleEntry, width=500)

    # draws the hint widgets and labels
    def drawHints(self):
        canvas = self.canvas
        # across label
        canvas.create_text(self.widthOfBoard, 110, text="Across", 
                           font="Helvetica 24 bold", anchor=W)
        # down label
        canvas.create_text(self.widthOfBoard, 330, text="Down",
                           font="Helvetica 24 bold", anchor=W)
        # across hints widget
        canvas.create_window(self.widthOfBoard, 125, anchor=NW, 
                             window=self.acrossFrame, width=350)
        # down hints widget
        canvas.create_window(self.widthOfBoard, 345, anchor=NW, 
                             window=self.downFrame, width=350)

    # draws the save buttons
    def drawSaveButtons(self):
        canvas = self.canvas
        # save with solution shape
        canvas.create_rectangle(self.widthOfBoard, 540, 762, 595, 
                                fill=self.selectedWordColor)
        # save with solution main text
        canvas.create_text(681, 560, text="Save", 
                           font="Helvetica 24 bold")
        # save with solution subtext
        canvas.create_text(681, 580, text="(with solution)", 
                           font="Helvetica 16")
        # save without solution shape
        canvas.create_rectangle(772, 540, 935, 595, 
                                fill=self.selectedWordColor)
        # save without solution main text
        canvas.create_text(853, 560, text="Save",
                           font="Helvetica 24 bold")
        # save without solution subtext
        canvas.create_text(853, 580, text="(without solution)", 
                           font="Helvetica 16")

    # initalizes the hint widgets (frame and scrollbar)
    def initHints(self):
        # across frame
        self.acrossFrame = Frame(self.canvas)
        # scrollbar to see all hints
        self.acrossScrollbar = Scrollbar(self.acrossFrame, orient=VERTICAL)
        # listbox so that users can select and edit individual lines
        # allow the scrollbar to change the y portion of the listbox
        self.acrossHints = Listbox(self.acrossFrame, font="Helvetica 16", 
                                   width=30, selectbackground=self.color,
                                   yscrollcommand=self.acrossScrollbar.set,
                                   height=9)
        self.acrossScrollbar.config(command=self.acrossHints.yview,)
        self.acrossScrollbar.pack(side=RIGHT, fill=Y)
        self.acrossHints.pack(side=LEFT, fill=BOTH, expand=1)        
        # down frame (same as across)
        self.downFrame = Frame(self.canvas)
        self.downScrollbar = Scrollbar(self.downFrame, orient=VERTICAL)
        self.downHints = Listbox(self.downFrame, font="Helvetica 16", width=30,
                              yscrollcommand=self.downScrollbar.set,
                              selectbackground=self.color, height=9)
        self.downScrollbar.config(command=self.downHints.yview)
        self.downScrollbar.pack(side=RIGHT, fill=Y)
        self.downHints.pack(side=LEFT, fill=BOTH, expand=1)

    # changes the hint of the active one with key pressed events
    def addHint(self, event, direction):
        if direction == "across":
            hintDir = self.acrossHints
        elif direction == "down":
            hintDir = self.downHints
        hint = hintDir.get(ACTIVE)
        # can only change the second part of the hint (not the number)
        for i in xrange(hintDir.size()):
            if hintDir.get(i) == hint:
                indexToActivate = i
        hint = hint.split("\t")
        # delete the last character
        if event.keysym == "BackSpace":
            hint[1] = hint[1][:-1]
        # add a space
        elif event.keysym == "space":
            hint[1] += " "
        # only add if a single letter
        elif len(event.keysym) == 1:
            hint[1] += event.keysym
        hint = "\t".join(hint)
        # maintain the same active hint
        hintDir.insert(ACTIVE, hint)
        hintDir.activate(indexToActivate)
        hintDir.delete(indexToActivate+1)

    # update the hints to show the correct numbers with direction
    def updateHints(self):
        self.acrossHints.delete(0, END)
        self.downHints.delete(0, END)
        for i in xrange(len(self.numDirsList)):
            text = "%s\t" % (self.numDirsList[i][0])
            if self.numDirsList[i][1] == "across":
                self.acrossHints.insert(END, text)
            elif self.numDirsList[i][1] == "down":
                self.downHints.insert(END, text)

    # initiaize the word suggestions widget
    def initWordSuggestions(self):
        # same as the across and down frame for the hints
        self.wordsFrame = Frame(self.canvas)
        self.wordsScrollbar = Scrollbar(self.wordsFrame, orient=VERTICAL)
        self.wordSuggestions = Listbox(self.wordsFrame, font="Helvetica 16", 
                                       width=30,
                                       yscrollcommand=self.wordsScrollbar.set,
                                       selectbackground=self.color,
                                       height=19)
        self.wordsScrollbar.config(command=self.wordSuggestions.yview)
        self.wordsScrollbar.pack(side=RIGHT, fill=Y)
        self.wordSuggestions.pack(side=LEFT, fill=BOTH, expand=1)

    # draw the possible words widget and labels
    def drawPossibleWords(self):
        canvas = self.canvas
        # word suggestions label
        canvas.create_text(self.widthOfBoard, 110, anchor=W, 
                           text="Word Suggestions", font="Helvetica 24 bold")
        # word suggestions widget
        canvas.create_window(self.widthOfBoard, 125, anchor=NW, 
                             window=self.wordsFrame)
        # button to advance to hints shape
        canvas.create_rectangle(self.widthOfBoard, 540, 840, 595, 
                                fill=self.selectedWordColor)
        # button to advance to hints text
        canvas.create_text(720, 568, text="Write Hints", 
                           font="Helvetica 24 bold")

    # draws the crossword board
    def drawCrosswordBoard(self):
        canvas = self.canvas
        for row in xrange(self.blocks):
            for col in xrange(self.blocks):
                # coordinates of each cell
                top = self.margin*2 + row*self.blockWidth
                left = self.margin + col*self.blockWidth
                bottom = top + self.blockWidth
                right = left + self.blockWidth                
                color = self.color
                # if the cell is 1, set color to black
                if self.board[row][col] == 1:
                    color = "black"
                canvas.create_rectangle(left, top, right, bottom, fill=color)

    # draws the selected letter
    def drawSelectedLetter(self):
        canvas = self.canvas
        top = self.margin*2 + self.selectedRow*self.blockWidth
        left = self.margin + self.selectedCol*self.blockWidth
        bottom = top + self.blockWidth
        right = left + self.blockWidth
        canvas.create_rectangle(left, top, right, bottom, 
                                fill=self.selectedLetterColor)

    # draws the selected word based on direction
    def drawSelectedWord(self):
        if self.direction == "across":
            self.drawSelectedWordAcross()
        elif self.direction == "down":
            self.drawSelectedWordDown()

    # draws the selected word if it is across
    def drawSelectedWordAcross(self):
        canvas = self.canvas
        # going to the right of the selected cell
        for col in xrange(self.selectedCol + 1, self.blocks):
            # stop drawing in direction if cell is black
            if self.board[self.selectedRow][col] == 1:
                break
            top = self.margin*2 + self.selectedRow*self.blockWidth
            left = self.margin + col*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)
        # going to the left of selected cell
        for col in xrange(self.selectedCol - 1, -1, -1):
            # stop drawing in direction if cell is black
            if self.board[self.selectedRow][col] == 1:
                break
            top = self.margin*2 + self.selectedRow*self.blockWidth
            left = self.margin + col*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)

    # draws the selected word if it is down
    def drawSelectedWordDown(self):
        canvas = self.canvas
        # going down from the selected cell
        for row in xrange(self.selectedRow + 1, self.blocks):
            # stop drawing in direction if cell is black
            if self.board[row][self.selectedCol] == 1:
                break
            top = self.margin*2 + row*self.blockWidth
            left = self.margin + self.selectedCol*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)
        # going up from the selected cell
        for row in xrange(self.selectedRow - 1, -1, -1):
            # stop drawing in direction if cell is black
            if self.board[row][self.selectedCol] == 1:
                break
            top = self.margin*2 + row*self.blockWidth
            left = self.margin + self.selectedCol*self.blockWidth
            bottom = top + self.blockWidth
            right = left + self.blockWidth
            canvas.create_rectangle(left, top, right, bottom, 
                                    fill=self.selectedWordColor)

    # draws the letters in each of the blocks (only if not None and 1)
    def drawWords(self):
        canvas = self.canvas
        for row in xrange(self.blocks):
            for col in xrange(self.blocks):
                # x, y are middle of the current cell (centering)
                x = self.margin + col*self.blockWidth + self.blockWidth/2
                y = self.margin*2 + row*self.blockWidth + self.blockWidth/2
                if self.board[row][col] != 1 and self.board[row][col] != None:
                    # all letters are uppercase
                    letter = self.board[row][col]
                    letter = letter.upper()
                    # find the color of the word (black or red)
                    color = self.colorOfLetters[row][col]
                    canvas.create_text(x, y, text=letter, font="Helvetica 22",
                                       fill=color)

    # draws the tiny numbers in the corner of the boxes
    def drawNumbers(self):
        canvas = self.canvas
        for i in xrange(len(self.numberList)):
            # find the row and col of each number
            row, col = self.numberList[i]
            # margin from the left side of the box
            numberSpacing = 3
            x = self.margin + col*self.blockWidth + numberSpacing
            y = self.margin*2 + row*self.blockWidth
            canvas.create_text(x, y, text=i+1, font="Helvetica 12", 
                               anchor=NW)

    # updates the board every time an event occurs while creating
    def onEvent(self):
        if self.mode == 0:
            self.updateTitle()
            self.wordList = self.findWords()
            self.numberList = self.findNumbers()
            self.checkWordsAreLegal()
            if self.suggestWords:
                self.possibleWords = self.findPossibleWords()
                self.updatePossibleWords()
            else:
                self.numDirsList = self.findNumberDirections()  

    # updates the words in the possible words widget
    def updatePossibleWords(self):
        # delete everything then add in all of the possible words
        self.wordSuggestions.delete(0, END)
        for word in self.possibleWords:
            self.wordSuggestions.insert(END, word)
        # if there are no possible words, indicate that
        if self.possibleWords == []:
            self.wordSuggestions.insert(END, "None")

    # chceks if a word is legal by the dictionary and changes its corresponding
    # color if it is not a real word
    def checkWordsAreLegal(self):
        for wordIndexes in self.wordList:
            word = []
            for rowLetter, colLetter in wordIndexes:
                word.append(self.board[rowLetter][colLetter])
            # if it is a complete word (don't bother checking incomplete words)
            if None not in word:
                word = "".join(word)
                # get definition of word (should exist if legal word)
                isWord = self.wordApi.getDefinitions(word, useCanonical=True)
                # if word has a definition, set it to black
                if isWord != None:
                    for row, col in wordIndexes:
                        self.colorOfLetters[row][col] = self.wordColor
                # else, set it to red (error)
                else:
                    for row, col in wordIndexes:
                        self.colorOfLetters[row][col] = self.errorColor

    # finds the words across recursively
    def findWordsAcross(self, wordList=None, row=0, col=0):
        # init wordList to avoid mutable param
        if wordList == None:
            wordList = []
        # if past the bottom of the board, return the word list
        if row >= self.blocks:
            return wordList
        # if at the end of a row, find words in the next row
        elif col > self.blocks - 1:
            return self.findWordsAcross(wordList, row+1, 0)
        # if the cell is black, go to the next column
        elif self.board[row][col] == 1:
            return self.findWordsAcross(wordList, row, col+1)
        # else, the current cell is blank and is a part of the board
        else:
            word = []
            # go to the right starting from that column
            for column in xrange(col, self.blocks):
                # until you hit a black square
                if self.board[row][column] == 1:
                    # if the word is longer than 1 character, add it to the list
                    if len(word) > 1:
                        wordList.append(word)
                    return self.findWordsAcross(wordList, row, column+1)
                # otherwise, add to the current word
                else:
                    word.append((row, column))
            # if you haven't hit a black square, still add the word to the list
            # if it is greater than len 1
            if len(word) > 1:
                wordList.append(word)
            # go to the next row
            return self.findWordsAcross(wordList, row+1, 0)

    # same as findWordsAcross except for checking at end of column instead of
    # end of row, and advances to start of next column when at the end of one
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

    # returns a list of numbers and their coordinates
    def findNumbers(self):
        numberList = []
        for i in xrange(len(self.wordList)):
            number = self.wordList[i][0]
            # do not want duplicates since there can be overlap
            if number not in numberList:
                numberList.append(number)
        return numberList

    # returns a list of numbers with the associated directions for creating
    # the hints (which number corresponds to which direction)
    # goes through each list of numbers and words and finds where the number
    # coordinates are in the word coordinates
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

    # taken from class notes
    def readFile(self, filename, mode="rt"):
        with open(filename, mode) as fin:
            return fin.read()

    # draws the help screen
    def drawHelpScreen(self):
        canvas = self.canvas
        # instructions text
        canvas.create_text(self.instructionX, self.instructionY, anchor=NW, 
                           text=self.instructions, font="Helvetica 16")
        # main menu shape
        canvas.create_rectangle(0, 0, self.mainMenuWidth, self.borderHeight,
                                fill=self.selectedWordColor)
        # title text
        canvas.create_text(self.cx, self.borderHeight/2, text="Instructions", 
                           font="Helvetica 24 bold")
        # main menu text
        canvas.create_text(self.mainMenuWidth/2, self.borderHeight/2, 
                           text="Back to Main Menu", font="Helvetica 20")

CrosswordCreator().run()