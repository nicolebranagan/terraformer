from PIL import Image
import math
import pixelgrid

class ColorSet:
    def __init__(self, maxcolors):
        self.maxcolors = maxcolors
        self.colors = []
    
    @property
    def palette(self):
        if len(self.colors) == self.maxcolors:
            return list(self.colors)
        else:
            c = list(self.colors)
            while (len(c) != self.maxcolors):
                c.append((0,0,0))
            return c

    def _maintain(self):
        if len(self.colors) <= self.maxcolors:
            # No need
            return

        #distmat = [[_colordist(c, x) for x in self.colors] 
        #           for c in self.colors]
        
        mindist = _colordist((0,0,0),
                             (256,256,256))
        closest1 = 0
        closest2 = 1

        for i, c in enumerate(self.colors):
            for j, k in enumerate(self.colors):
                if i == j:
                    continue

                dist = _colordist(c, k)
                if (dist < mindist):
                    mindist = dist
                    closest1 = i
                    closest2 = j

        newcolor = _averagecolor(self.colors[closest1], 
                                 self.colors[closest2])
        self.colors.pop(max(closest2,closest1))
        self.colors.pop(min(closest1,closest2))
        self.colors.append(newcolor)
        self._maintain()

    def addColor(self, color):
        color = color[0:3]
        if color not in self.colors:
            self.colors.append(color)
            self._maintain()
    
    def nearestIndex(self, color):
        color = color[0:3]
        dist = [(_colordist(color, j), i) for i,j in enumerate(self.colors)]
        return min(dist)[1]
        #nearest = self.colors[0]
        #mindist = _colordist((0,0,0),
        #                     (256,256,256))
        #for c in self.colors:
        #    dist = _colordist(c, color)

def _colordist(color1, color2):
    return (_square(color1[0] - color2[0]) +
            _square(color1[1] - color2[1]) +
            _square(color1[2] - color2[2]))

def _averagecolor(color1, color2):
    return ( math.floor((color1[0] + color1[0]) / 3),
             math.floor((color1[1] + color1[1]) / 3),
             math.floor((color1[2] + color1[2]) / 3) )

def _square(a):
    return a*a

def importpixelgrid(filen):
    colors = ColorSet(16)
    image = Image.open(filen).convert("RGB")
    
    # Build palette
    for i in range(0, min(image.width, 256)):
        for j in range(0, min(image.height, 256)):
            pixel = image.getpixel((i,j))
            colors.addColor(pixel)

    grid = pixelgrid.PixelGrid(colors.palette)
    
    for i in range(0, min(image.width, 256)):
        for j in range(0, min(image.height, 256)):
            pixel = image.getpixel((i,j))
            val = colors.nearestIndex(pixel)
            if val != 0:
                grid.set(i,j,val)

    return grid
