# crossword.py
# Dylan Steele + dylans + Section D

from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass
from dictionaryClass import Dictionary
import tkMessageBox, tkSimpleDialog
import cPickle

class CrosswordPuzzle(EventBasedAnimationClass):

    def __init__(self, blocksPerSide=15):
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
        self.dictionary = Dictionary().dictionary
        # mode 0 is creating crossword
        # mode 1 is solving crossword
        self.mode = None
        self.isMenuScreen = True
        self.isHelpScreen = False
        self.color = "Ivory"
        self.selectedWordColor = "DodgerBlue2"
        self.selectedLetterColor = "Gold"
        self.selectedRow = None
        self.selectedCol = None
        self.message = ""
        # self.initMenuButtons()
        self.initCreateMode()

    # def initMenuButtons(self):
    #     self.createButton = Button(self.canvas, text="Create", 
    #                                command=self.onCreateButtonPressed)
    #     self.solveButton = Button(self.canvas, text="Solve", 
    #                               command=self.onSolveButtonPressed)
    #     self.helpButton = Button(self.canvas, text="Help", 
                                 # command=self.onHelpButtonPressed)

    def onCreateButtonPressed(self):
        self.isMenuScreen = False
        self.mode = 0

    def onSolveButtonPressed(self):
        self.isMenuScreen = False
        self.mode = 1

    def onHelpButtonPressed(self):
        self.isMenuScreen = False
        self.isHelpScreen = True

    def onRightClick(self, event):
        if self.mode == 0: #create mode
            if (self.margin <= event.x <= self.blockWidth*self.blocks + 
                self.margin) and (self.margin*2 <= event.y <= self.blockWidth*
                self.blocks + self.margin*2):
                row, col = self.getSelectedRowAndCol(event)
                if self.board[row][col] == None:
                    self.board[row][col] = 1
                    self.board[-row-1][-col-1] = 1
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
            pass

    def onClickInMenu(self, event):
        # lots of magic numbers, will fix when menu screen style is finalyzed
        cx = self.width / 2
        if (cx - 80) <= event.x <= (cx + 80) and (200 <= event.y <= 280):
            # self.createCrosswordMode()
            self.isMenuScreen = False
            self.mode = 0
        elif (cx - 80) <= event.x <= (cx + 80) and (300 <= event.y <= 380):
            # self.solveCrosswordMode()
            self.isMenuScreen = False
            self.mode = 1
        elif (cx - 80) <= event.x <= (cx + 80) and (400 <= event.y <= 480):
            self.isMenuScreen = False
            self.isHelpScreen = True

    def onKeyPressed(self, event):
        print event.keysym, "pressed"

    def redrawAll(self):
        self.canvas.delete(ALL)
        if self.isMenuScreen:
            self.drawMenuScreen()
        elif self.isHelpScreen:
            self.drawHelpScreen()
        elif self.mode == 0: #create mode
            self.drawCreateMode()
        elif self.mode == 1: #solve mode
            # self.initSolveMode()
            self.drawSolveMode()

    def drawMenuScreen(self):
        # lots of magic numbers, will fix when menu screen style is finalyzed
        canvas = self.canvas
        cx = self.width / 2
        canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        canvas.create_text(cx, self.margin, text="Crosswordr",
                           font="Arvo 48 bold")
        canvas.create_text(cx, self.margin*2, text="Dylan Steele",
                           font="Arvo 28")
        canvas.create_rectangle(cx-80, 200, cx+80, 280, 
                                fill=self.selectedWordColor)
        canvas.create_text(cx, 240, text="Create", font="Arvo 28 bold")
        canvas.create_rectangle(cx-80, 300, cx+80, 380, fill=self.selectedWordColor)
        canvas.create_text(cx, 340, text="Solve", font="Arvo 28 bold")
        canvas.create_rectangle(cx-80, 400, cx+80, 480, fill=self.selectedWordColor)
        canvas.create_text(cx, 440, text="Help", font="Arvo 28 bold")
        # canvas.create_window(cx, 200, window=self.createButton)
        # canvas.create_window(cx, 300, window=self.solveButton)
        # canvas.create_window(cx, 400, window=self.helpButton)

    def initCreateMode(self):
        self.title = "Title"
        self.board = [[None]*self.blocks for i in xrange(self.blocks)]

    def drawCreateMode(self):
        # self.drawTitle()
        self.drawCrosswordBoard()
    
    def drawCrosswordBoard(self):
        self.board[0][1] = 1
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

        

    def button1Pressed(self):
        # AskString Box
        message = "How many blocks would you like?"
        title = "AskInt Box"
        options = range(7, 15)
        response = tkSimpleDialog.askstring(title, message)
        # response = choose(message, title, options)
        message = "You just answered: " + str(response)
        title = "Response (Info box)"
        tkMessageBox.showinfo(title, message)

    def choose(message, title, options):
        msg = message + "\n" + "Choose one:"
        for i in xrange(len(options)):
            msg += "\n" + str(i+1) + ": " + options[i]
        response = tkSimpleDialog.askstring(title, msg)
        return options[int(response)-1]

CrosswordPuzzle().run()



