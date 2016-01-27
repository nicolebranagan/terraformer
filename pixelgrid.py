import math
import tkinter as tk

class PixelGrid:
    def __init__(self, palette):
        # Declare an empty pixelgrid
        self._width = 32
        self._height = 32
        self._tiles = {}
        self.palette = palette

    def get(self, x, y):
        tilex = x // 8
        tiley = y // 8
        relx = x - tilex*8
        rely = y - tiley*8
        
        if ( (tilex, tiley) in self._tiles):
            return self._tiles[(tilex,tiley)].get(relx, rely)
        else:
            return 0

    def getColor(self, x, y):
        return self.palette[self.get(x,y)]

    def set(self, x, y, val):
        tilex = x // 8
        tiley = y // 8
        relx = x - tilex*8
        rely = y - tiley*8

        if ( (tilex, tiley) not in self._tiles):
            self._tiles[(tilex,tiley)] = PixelTile()

        self._tiles[(tilex,tiley)].set(relx, rely, val)

    def clearTile(self, x, y): 
        self._tiles.pop((x,y),None)

    def getTkImage(self, zoom):
        photo = tk.PhotoImage(width=8*self._width*zoom, 
                              height=8*self._height*zoom)
        photo.put("#%02x%02x%02x" % self.palette[0], 
                  to=(0,0,8*self._width*zoom,8*self._height*zoom))
        for i in range(0, 8*self._width):
            for j in range(0, 8*self._height):
                if self.get(i,j) != 0:
                    photo.put(
                        "#%02x%02x%02x" % self.getColor(i,j), 
                        to=(i*zoom, j*zoom,i*zoom+(zoom), j*zoom+(zoom)))
        return photo

    def getTkSubset(self, zoom, x, y, r):
        photo = tk.PhotoImage(width=8*r*zoom, 
                              height=8*r*zoom)
        photo.put("#%02x%02x%02x" % self.palette[0], 
                  to=(0,0,8*r*zoom,8*r*zoom))
        for i in range(0, 8*r):
            for j in range(0, 8*r):
                if self.get(i + x*8,j + y*8) != 0:
                    photo.put(
                        "#%02x%02x%02x" % self.getColor(i + x*8,j + y*8), 
                        to=(i*zoom, j*zoom,i*zoom+(zoom), j*zoom+(zoom)))
        return photo

class PixelTile:
    def __init__(self):
        self._width = 8
        self._height = 8
        self._pixels = [0 for x in range(self._width * self._height)]

    def get(self, x, y):
        return self._pixels[x + y*self._width]

    def set(self, x, y, val):
        self._pixels[x + y*self._width] = val

class PixelSubset(PixelGrid):
    def __init__(self, parent, selection):
        self.parent = parent
        self.palette = parent.palette
        minx = min(selection[0], selection[2])
        maxx = max(selection[0], selection[2])
        miny = min(selection[1], selection[3])
        maxy = max(selection[1], selection[3])
        self._width = maxx-minx
        self._height = maxy-miny
        self._tiles = {}

        for i in range(0, parent._width):
            for j in range(0, parent._height):
                if i >= minx and i <= maxx and j >= miny and j <= maxy:
                    if (i,j) in parent._tiles:
                        self._tiles[(i-minx, j-miny)] = parent._tiles[(i,j)]



