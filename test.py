# test.py

from Tkinter import *
from seventBasedAnimationClass import EventBasedAnimationClass

class Test(EventBasedAnimationClass):
    def __init__(self):
        super(Test, self).__init__(1000, 650)

    def initAnimation(self): 
        self.acrossFrame = Frame(self.canvas)
        self.acrossScrollbar = Scrollbar(self.acrossFrame, orient=VERTICAL)
        self.acrossHints = Listbox(self.acrossFrame, font="Helvetica 16", width=30,
                                yscrollcommand=self.acrossScrollbar.set)
        self.acrossScrollbar.config(command=self.acrossHints.yview,)
        self.acrossScrollbar.pack(side=RIGHT, fill=Y)
        self.acrossHints.pack(side=LEFT, fill=BOTH, expand=1)
        for i in xrange(100):
            self.acrossHints.insert(END, i)

        self.downFrame = Frame(self.canvas)
        self.downScrollbar = Scrollbar(self.downFrame, orient=VERTICAL)
        self.downHints = Listbox(self.downFrame, font="Helvetica 16", width=30,
                                yscrollcommand=self.downScrollbar.set)
        self.downScrollbar.config(command=self.downHints.yview,)
        self.downScrollbar.pack(side=RIGHT, fill=Y)
        self.downHints.pack(side=LEFT, fill=BOTH, expand=1)
        for i in xrange(100):
            self.downHints.insert(END, i)

    def redrawAll(self):
        self.canvas.create_window(600, 50, anchor=NW, window=self.acrossFrame)
        self.canvas.create_window(100, 50, anchor=NW, window=self.downFrame)
        self.canvas.create_text(200, 400, text="hello", font="Arial 20")

Test().run()