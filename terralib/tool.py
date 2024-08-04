from terralib.pixelgrid import *
import math
import copy
import queue

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

def undoblock(selection):
    global pixelgrid
    selection = copy.copy(selection)
    block = PixelSubset(pixelgrid, selection)
    def reverse():
        pixelgrid.mergeSubset(block, selection[0], selection[1])
        redraw()
    undostack.append(reverse)

def undoscreen():
    global pixelgrid
    oldgrid = copy.deepcopy(pixelgrid)
    def reverse():
        global pixelgrid
        pixelgrid.mergeSubset(oldgrid,0,0)
        redraw()
    undostack.append(reverse)

def undopalette():
    global pixelgrid
    oldpalette = copy.copy(pixelgrid.palette)
    def reverse():
        global pixelgrid
        pixelgrid.palette = oldpalette
        redraw(True, True, True)
    undostack.append(reverse)

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
            global pixelgrid
            global redraw
            pixelgrid.set(tilex*8 + x, tiley*8 + y, val2)
            redraw()

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
    def __init__(self, alternate, filled):
        self.twostep = True
        self.alternate = alternate
        self.filled = filled 
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
        
        # Make sure first cell is always drawn in a dithering situation
        todraw = (x1 + y1) % 2

        redraw()
        for i in range(mx1, mx2):
            for j in range(my1, my2):
                if ((self.filled and (not self.alternate or 
                    (self.alternate and (i + j) % 2 == todraw))) or
                    (not self.filled and (i == mx1 or i == mx2-1 or 
                                     j == my1 or j == my2-1))):
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

        # Make sure first cell is always drawn in a dithering situation
        todraw = (x1 + y1) % 2

        for i in range(mx1, mx2):
            for j in range(my1, my2):
                if ((self.filled and (not self.alternate or 
                    (self.alternate and (i + j) % 2 == todraw))) or
                    (not self.filled and (i == mx1 or i == mx2-1 or 
                                          j == my1 or j == my2-1))):
                    pixelgrid.set(tilex*8 + i,tiley*8 + j,val)
        
        redraw()

class Line(Tool):
    def __init__(self):
        self.twostep = True
        self.pixel = True

    def _step1(self, tilex, tiley, x, y, val):
        self.x1 = x
        self.y1 = y

    def move(self, tilex, tiley, x2, y2, val):
        redraw()
        self.approximate_line(lambda x,y: quickdraw(x, y, val),
                              x2, y2)

    def _step2(self, tilex, tiley, x2, y2, val):
        undoblock([ tilex + math.floor(min(self.x1, x2)/8),
                    tiley + math.floor(min(self.y1, y2)/8),
                    tilex + math.ceil(max(self.x1, x2)/8),
                    tiley + math.ceil(max(self.y1, y2)/8) ])
        def draw_point(x,y):
            quickdraw(x, y, val)
            pixelgrid.set(tilex*8 + x, tiley*8 + y, val)
        
        self.approximate_line(draw_point, x2, y2)
        redraw()

    def approximate_line(self, func, x2, y2):
        if x2 == self.x1:
            # Straight line
            for y in range(self.y1, y2):
                func(x2, y)
            return

        # Bresenham algorithm
        delx = x2 - self.x1
        dely = y2 - self.y1
        error = 0.0
        err = abs(dely / delx)
        y = self.y1
        yshift = math.floor(math.copysign(1, y2-self.y1))
        xshift = math.floor(math.copysign(1, x2-self.x1))

        for x in range(self.x1, x2, xshift):
            func(x,y)
            error = error + err
            while error >= 0.5:
                func(x,y)
                y = y + yshift
                error = error - 1.0

class Shifter:
    def __init__(self, dx, dy):
        self.twostep = False
        self.pixel = False
        self.dx = dx
        self.dy = dy

    def step1(self, selection):
        global pixelgrid
        global redraw
        undoblock(selection)
        block = PixelSubset(pixelgrid, selection)
        block.shift(self.dx, self.dy)
        pixelgrid.mergeSubset(block, selection[0], selection[1])
        redraw()

class LinearFunc:
    def __init__(self, a, b, c, d, e, f):
        self.twostep = False
        self.pixel = False
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def step1(self, selection):
        global pixelgrid
        global redraw
        undoblock(selection)
        block = PixelSubset(pixelgrid, selection)
        block.linearshift(self.a, self.b, self.c, self.d, self.e, self.f)
        pixelgrid.mergeSubset(block, selection[0], selection[1])
        redraw()

class Fill(Tool):
    def __init__(self):
        self.twostep = False
        self.pixel = True

    def _step1(self, tilex, tiley, x, y, val):
        global pixelgrid
        undoscreen()
        val0 = pixelgrid.get(tilex*8 + x, tiley*8 + y)
        val1 = val0
        x = tilex*8 + x
        y = tiley*8 + y
        edge = [(x,y)]
        pixelgrid.set(x, y, val)
        while True:
            newedge = []
            for (x,y) in edge:
                for (i,j) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if pixelgrid.bounds(i,j) and \
                        pixelgrid.get(i,j) == val0:
                        pixelgrid.set(i,j,val)
                        newedge.append((i,j))
            edge = newedge
            if len(edge) == 0 or len(edge)>500:
                break
        redraw()
            
class FilledCircle(Tool):
    def __init__(self):
        self.twostep = True
        self.pixel = True

    def _step1(self, tilex, tiley, x, y, val):
        self.x1 = x
        self.y1 = y

    def move(self, tilex, tiley, x2, y2, val):
        redraw()
        self.approximate_circ(lambda x,y: quickdraw(x, y, val),
                              x2, y2)

    def _step2(self, tilex, tiley, x2, y2, val):
        undoscreen()
        def draw_point(x,y):
            quickdraw(x, y, val)
            pixelgrid.set(tilex*8 + x, tiley*8 + y, val)
        
        self.approximate_circ(draw_point, x2, y2)
        redraw()

    def approximate_circ(self, func, x2, y2):
        x_1 = min(self.x1, x2)
        y_1 = min(self.y1, y2)
        x_2 = max(self.x1, x2)
        y_2 = max(self.y1, y2)
        xdiam = x_2 - x_1
        ydiam = y_2 - y_1
        diam = max(xdiam, ydiam)
        r = round(diam/2)
        xc = x_1 + r
        yc = y_1 + r
        r2 = r*r
        
        x = 0
        y = round(math.sqrt(r2 - x*x) + 0.5)
        
        while x < y:
            func(xc+x, yc+y)
            func(xc+x, yc-y)
            func(xc-x, yc+y)
            func(xc-x, yc-y)
            func(xc+y, yc+x)
            func(xc+y, yc-x)
            func(xc-y, yc+x)
            func(xc-y, yc-x)
            x = x + 1
            y = round(math.sqrt(r2 - x*x) + 0.5)
        if x == y:
            func(xc + x, yc + y)
            func(xc + x, yc - y)
            func(xc - x, yc + y)
            func(xc - x, yc - y)

class Circle(FilledCircle):
    def approximate_circ(self, func, x2, y2):
        x_1 = min(self.x1, x2)
        y_1 = min(self.y1, y2)
        x_2 = max(self.x1, x2)
        y_2 = max(self.y1, y2)
        xdiam = x_2 - x_1
        ydiam = y_2 - y_1
        diam = max(xdiam, ydiam)
        r = round(diam/2)
        xc = x_1 + r
        yc = y_1 + r
        r2 = r*r
        
        for x in range(0, r):
            for y in range(0, r):
                if (x*x + y*y) < r*r:
                    func(xc+x, yc+y)
                    func(xc-x, yc+y)
                    func(xc+x, yc-y)
                    func(xc-x, yc-y)

class Shadowize:
    def __init__(self, selectedcolor, basezoom):
        self.twostep = False
        self.pixel = False
        self.selectedcolor = selectedcolor
        self.basezoom = basezoom

    def step1(self, selection):
        global pixelgrid
        global redraw
        print(self.basezoom)
        undoblock(selection)
        block = PixelSubset(pixelgrid, selection)
        for x in range(0, 8*block.width):
            for y in range(0, 8*block.height):
                if x % (8*self.basezoom) == (8*self.basezoom - 1):
                    continue
                if y % (8*self.basezoom) == (8*self.basezoom - 1):
                    continue
                potential_tile = block.get(x,y)
                potential_shadow = block.get(x+1,y+1)
                if potential_tile == 0:
                    continue
                if potential_shadow != 0:
                    continue
                if potential_tile == self.selectedcolor:
                    continue
                block.set(x+1, y+1, self.selectedcolor)
        pixelgrid.mergeSubset(block, selection[0], selection[1])
        redraw()
