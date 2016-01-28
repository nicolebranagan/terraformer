from pixelgrid import *

pixelgrid = None
quickdraw = None
redraw = None
undostack = []

def initialize(grid, quick, re):
    global pixelgrid 
    pixelgrid = grid
    global quickdraw 
    quickdraw = quick
    global redraw 
    redraw = re
    global undostack 
    undostack = []

def undo(event=None):
    if len(undostack) != 0:
        f = undostack.pop()
        f()

class Tool:
    def __init__(self):
        # Does the tool take two steps to complete?
        self.twostep = False
        # Does the tool act on a full image or a pixel?
        self.pixel = False

    # Step 1 method, called on first click.
    def step1(self, tilex, tiley, x, y, val):
        if (pixelgrid is None):
            return
        else:
            self._step1(tilex, tiley, x, y, val)
    
    def step2(self, tilex, tiley, x1, y1, x2, y2, val):
        self._step2(tilex, tiley, x1, y1, x2, y2, val)
        undostack.append(self.reverse)

    def _step1(self, tilex, tiley, x, y, val):
        pass
    
    def _step2(self, tilex, tiley, x1, y1, x2, y2, val):
        pass

    def reverse(self):
        pass

class Pencil(Tool):
    def __init__(self, alternate):
        self.twostep = False
        self.alternate = alternate
        self.pixel = True
        self.last = (-1, -1, -1)

    def _step1(self, tilex, tiley, x, y, val):
        if self.alternate and (x + y) % 2 == 1:
            return
        val2 = pixelgrid.get(tilex*8 + x, tiley*8 + y)
        newlast = (tilex*8 + x, tiley*8 + y, val)
        if val == val2:
            return
        if newlast == self.last:
            return
        self.last = newlast
        pixelgrid.set(tilex*8 + x, tiley*8 + y, val)
        quickdraw(x, y, val)
        
        def rev():
            pixelgrid.set(tilex*8 + x, tiley*8 + y, val2)
            quickdraw(x, y, val2)

        global undostack
        undostack.append(rev)
       
class Delete(Tool):
    def __init__(self):
        self.twostep = False
        self.pixel = False
        self.last = (-1, -1, -1, -1)
        self.block = None

    def _step1(self, tilex, tiley, x, y, val):
        global pixelgrid
        newlast = (tilex, tiley, x, y) 
        if newlast == self.last:
            return
        else:
            self.last = newlast
        self.block = PixelSubset(pixelgrid, [tilex, tiley, x, y])
        
        def rev():
            global pixelgrid
            global redraw
            pixelgrid.mergeSubset(self.block, self.last[0], self.last[1])
            redraw()
        undostack.append(rev)

        rangex = range(tilex, x)
        rangey = range(tiley, y)
        for i in rangex:
            for j in rangey:
                pixelgrid.clearTile(i,j)
        
        
