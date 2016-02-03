import math
import copy
import tkinter as tk

class PixelGrid:
    def __init__(self, palette):
        # Declare an empty pixelgrid
        self._width = 32
        self._height = 32

        self._tiles = {}

        self._pages = []
        self._pages.append(self._tiles)
        self.palette = palette

    @property
    def pages(self):
        return len(self._pages)

    def get(self, x, y, tileset=None):
        if tileset is None:
            tileset = self._tiles

        tilex = x // 8
        tiley = y // 8
        relx = x - tilex*8
        rely = y - tiley*8
        
        if ( (tilex, tiley) in tileset):
            return tileset[(tilex,tiley)].get(relx, rely)
        else:
            return 0

    def getColor(self, x, y):
        return self.palette[self.get(x,y)]

    def set(self, x, y, val):
        if x < 0 or x >= self._width*8 or y < 0 or y >= self._height*8:
            return

        tilex = x // 8
        tiley = y // 8
        relx = x - tilex*8
        rely = y - tiley*8

        if ( (tilex, tiley) not in self._tiles):
            self._tiles[(tilex,tiley)] = PixelTile()
        self._tiles[(tilex,tiley)].set(relx, rely, val)

    def clearTile(self, x, y): 
        self._tiles.pop((x,y),None)

    def bounds(self, x, y):
        return (x >= 0 and x < 8*self._width and 
                y >= 0 and y < 8*self._height)

    def mergeSubset(self, subset, x, y):
        for i in range(0, subset._width):
            for j in range(0, subset._height):
                if i + x <= self._width and j + y <= self._height:
                    if (i,j) in subset._tiles:
                        self._tiles[(i+x, j+y)] = subset._tiles[(i,j)]
                    else:
                        if (i+x, j+y) in self._tiles:
                            del(self._tiles[(i+x, j+y)])
    
    def flipColors(self, val1, val2, s):
        for i in range(s[0], s[2]):
            for j in range(s[1], s[3]):
                if (i,j) in self._tiles:
                    self._tiles[(i,j)].flip(val1, val2)
                elif val1 == 0:
                    self._tiles[(i, j)] = PixelTile(val2)

    def linearshift(self, a, b, c, d, e, f):
        oldtiles = copy.deepcopy(self._tiles)
        for x in range(0, 8*self._width):
            for y in range(0, 8*self._height):
                i = (a*x+b*y+c*(self._width*8-1))
                j = (d*x+e*y+f*(self._height*8-1))
                if (self.get(x, y, oldtiles) != self.get(i,j, oldtiles)):
                    self.set(i,j,self.get(x,y,oldtiles))

    def shift(self, dx, dy):
        oldtiles = copy.deepcopy(self._tiles)
        
        for i in range(0, 8*self._width):
            for j in range(0, 8*self._height):
                x = (i - dx) % (8*self._width)
                y = (j - dy) % (8*self._height)
                 
                if (self.get(x, y, oldtiles) != self.get(i,j, oldtiles)):
                    self.set(i,j,self.get(x,y,oldtiles))

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

    def dump(self):
        output = {}
        output["version"] = 0.0 # just in case we need it later
        output["width"] = self._width
        output["height"] = self._height
        output["palette"] = self.palette

        output["tiles"] = []
        i = -1
        for page in self._pages:
            i = i+1
            output["tiles"].append({})
            for c in page:
                st = "".join((str(c[0]),",",str(c[1])))
                output["tiles"][i][st] = page[c].dump()

        return output

    def load(self, info):
        self._pages = []
        self._width = int(info["width"])
        self._height = int(info["height"])
        self.palette = [tuple(x) for x in info["palette"]]
        
        i = -1
        for page in info["tiles"]:
            i = i+1
            self._pages.append({})
            for tile in page:
                num = tile.split(",")
                if len(num) != 2:
                    continue
                loc = (int(num[0]),int(num[1]))
                self._pages[i][loc] = PixelTile().load(page[tile])

        self._tiles = self._pages[0]

    def changepage(self, pagenum):
        while len(self._pages) < (pagenum+1):
            self._pages.append({})
        self._tiles = self._pages[pagenum]

class PixelTile:
    def __init__(self, fill=0):
        self._width = 8
        self._height = 8
        self._pixels = [fill for x in range(self._width * self._height)]

    def get(self, x, y):
        return self._pixels[x + y*self._width]

    def set(self, x, y, val):
        i = x+y*self._width
        self._pixels[x + y*self._width] = val

    def flip(self, val1, val2):
        self._pixels = [val2 if x == val1 else x for x in self._pixels]

    def dump(self):
        return self._pixels

    def load(self, pixels):
        self._pixels = pixels
        return self

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
                        self._tiles[(i-minx, j-miny)] = copy.deepcopy(
                                parent._tiles[(i,j)])



