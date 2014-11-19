# eventBasedAnimationClass.py

from Tkinter import *
import sys

class EventBasedAnimationClass(object):
    def onLeftClick(self, event): pass
    def onRightClick(self, event): pass
    def onKeyPressed(self, event): pass
    def onTimerFired(self): pass
    def redrawAll(self): pass
    def initAnimation(self): pass

    def __init__(self, width=300, height=300):
        self.width = width
        self.height = height
        self.timerDelay = 2000 # in milliseconds (set to None to turn off timer)

    def onLeftClickWrapper(self, event):
        if (not self._isRunning): return
        self.onLeftClick(event)
        self.redrawAll()

    def onRightClickWrapper(self, event):
        if (not self._isRunning): return
        self.onRightClick(event)
        self.redrawAll()

    def onKeyPressedWrapper(self, event):
        if (not self._isRunning): return
        self.onKeyPressed(event)
        self.redrawAll()

    def onTimerFiredWrapper(self):
        if (not self._isRunning): self.root.destroy(); return
        if (self.timerDelay == None): return # turns off timer
        self.onTimerFired()
        self.redrawAll()
        self.canvas.after(self.timerDelay, self.onTimerFiredWrapper)         

    def quit(self):
        if (not self._isRunning): return
        self._isRunning = False
        if (self.runningInIDLE):
            # in IDLE, must be sure to destroy here and now
            self.root.destroy()
        else:
            # not IDLE, then we'll destroy in the canvas.after handler
            self.root.quit()

    def run(self):
        # create the root and the canvas
        self.root = Tk()
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.initAnimation()
        self.canvas.pack()
        # set up events
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.quit())
        self._isRunning = True
        self.runningInIDLE =  ("idlelib" in sys.modules)
        # DK: You can use a local function with a closure
        # to store the canvas binding, like this:
        def leftClick(event): self.onLeftClickWrapper(event)    
        self.root.bind("<Button-1>", leftClick)
        def rightClick(event): self.onRightClickWrapper(event)
        self.root.bind("<Button-2>", rightClick)
        # DK: Or you can just use an anonymous lamdba function, like this:
        self.root.bind("<Key>", lambda event: self.onKeyPressedWrapper(event))
        self.onTimerFiredWrapper()
        # and launch the app (This call BLOCKS, so your program waits
        # until you close the window!)
        self.root.mainloop()
