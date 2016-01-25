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
        tilex = math.floor(x / 8)
        tiley = math.floor(x / 8)
        
        if ( (tilex, tiley) in self._tiles):
            return self.palette[self.get(x,y)]
        else:
            return self.palette[0]

    def set(self, x, y, val):
        tilex = x // 8
        tiley = x // 8
        relx = x - tilex*8
        rely = y - tiley*8
        
        if ( (tilex, tiley) not in self._tiles):
            self._tiles[(tilex,tiley)] = PixelTile()

        self._tiles[(tilex,tiley)].set(relx, rely, val)
    
    def getTkImage(self, zoom):
        photo = tk.PhotoImage(width=8*self._width*zoom, 
                              height=8*self._height*zoom)
        photo.put("#%02x%02x%02x" % self.palette[0], 
        #          to=(0,0,8*self._width*zoom,8*self._height*zoom))
                  to=(0,0,512,512))
        for i in range(0, 8*self._width):
            for j in range(0, 8*self._height):
                if self.getColor(i,j) != 0:
                    photo.put(
                        "#%02x%02x%02x" % self.getColor(i,j), 
                        to=(i*zoom, j*zoom,i*zoom+(zoom), j*zoom+(zoom)))
        print(8*self._width*zoom)
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

