from pixelgrid import *
import math
import copy

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
    
    def step2(self, tilex, tiley, x2, y2, val):
        self._step2(tilex, tiley, x2, y2, val)

    def _step1(self, tilex, tiley, x, y, val):
        pass

    def _move(self, tilex, tiley,x2, y2, val):
        pass

    def _step2(self, tilex, tiley, x2, y2, val):
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
        
class Rectangle(Tool):
    def __init__(self, alternate):
        self.twostep = True
        self.alternate = alternate
        self.pixel = True
        self.block = None

    def _step1(self, tilex, tiley, x, y, val):
        self.x1 = x
        self.y1 = y

    def move(self, tilex, tiley, x2, y2, val):
        global redraw
        global quickdraw
        
        x1 = self.x1
        y1 = self.y1

        if x1 == x2:
            x2 = x2 + 1
        elif x1 > x2:
            x1 = x1 + 1
        
        if y1 == y2:
            y2 = y2 + 1
        elif y1 > y2:
            y1 = y1 + 1
        
        mx1 = min(x2, x1)
        my1 = min(y2, y1)
        mx2 = max(x2, x1)
        my2 = max(y2, y1)
        
        redraw()
        for i in range(mx1, mx2):
            for j in range(my1, my2):
                if not self.alternate or (i + j) % 2 == 0:
                    quickdraw(i,j,val)
            
    
    def _step2(self, tilex, tiley, x2, y2, val):
        global pixelgrid
        global redraw
        
        x1 = self.x1
        y1 = self.y1

        if x1 == x2:
            x2 = x2 + 1
        elif x1 > x2:
            x1 = x1 + 1
        
        if y1 == y2:
            y2 = y2 + 1
        elif y1 > y2:
            y1 = y1 + 1
        
        mx1 = min(x2, x1)
        my1 = min(y2, y1)
        mx2 = max(x2, x1)
        my2 = max(y2, y1)
        
        block = PixelSubset(
            pixelgrid, [
                tilex + math.floor(mx1 / 8),
                tiley + math.floor(my1 / 8),
                tilex + math.ceil(mx2 / 8),
                tiley + math.ceil(my2 / 8),
                ])
        
        def rev():
            global pixelgrid
            global redraw
            pixelgrid.mergeSubset(block, tilex, tiley)
            redraw()
        undostack.append(rev)

        for i in range(tilex*8 + mx1, tilex*8 + mx2):
            for j in range(tiley*8 + my1, tiley*8 + my2):
                if not self.alternate or (i + j) % 2 == 0:
                    pixelgrid.set(i,j,val)
        
        redraw()



