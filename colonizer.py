# Colonizer is not intended for use yet
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import json
import math
import os

from terralib.pixelgrid import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack()

        self.tilegrid = TileGrid()

        self.createWidgets()

    def createWidgets(self):
        # Create menu
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)

        # Create loading buttons
        loadframe = tk.Frame(self)
        loadframe.grid(row=0, column=0, sticky=tk.W)
        openbutton = tk.Button(loadframe, text="Open", command=self.open)
        openbutton.grid(row=0, column=0)
        self.loadergrid = tk.StringVar()
        self.loadergrid.trace("w", self.changegrid)
        self.loader = tk.OptionMenu(
                loadframe, self.loadergrid, "Nothing loaded")
        self.loader.grid(row=0, column=1)
        self.pageflip = Flipper(self, onchange=self.changepage)
        self.pageflip.grid(row=0, column=1, sticky=tk.E)

        # Create panels
        self.tilepalette = tk.Canvas(self, width=512, height=512)
        self.tilepalette.grid(row=1, column=0, columnspan=2)
        self.tilepaletteimage = self.tilepalette.create_image(
                0, 0, anchor=tk.NW)
        
        self.tileimg = tk.Canvas(self, width=512, height=512)
        self.tileimg.grid(row=1, column=2)
        self.tileimgimage = self.tileimg.create_image(
                0, 0, anchor=tk.NW)
        self.tileimg.bind("<Button-1>", self.clicktileimg)

    def open(self):
        filen = filedialog.askopenfilename(
                filetypes=(("Terraformer images", "*.terra"),
                           ("All files", "*")),
                title="Open paletted image")
        if filen != () and filen != "":
            with open(filen, "r") as fileo:
                pixelgrid = PixelGrid([(0,0,0)])
                pixelgrid.load(json.load(fileo))
                name = os.path.basename(filen)
                self.tilegrid.add_dependency(filen, pixelgrid)
                self.resetgrids()

    def changegrid(self, *args):
        self.currentgrid = self.tilegrid.get_grid(self.loadergrid.get())
        self.tilepalettetkimg = self.currentgrid.getTkImage(2)
        self.tilepalette.itemconfig(self.tilepaletteimage, 
                                    image=self.tilepalettetkimg)
        self.pageflip.top = self.currentgrid.pages - 1
        self.pageflip.value = 0
        self.pageflip.reset()
        self.currentgrid.changepage(0)

    def resetgrids(self):
        self.loader["menu"].delete(0, "end")
        for key in self.tilegrid.dependencies:
            self.loader["menu"].add_command(label=key, command=tk._setit(
                        self.loadergrid, key))

    def changepage(self):
        self.currentgrid.changepage(self.pageflip.value)
        self.tilepalettetkimg = self.currentgrid.getTkImage(2)
        self.tilepalette.itemconfig(self.tilepaletteimage, 
                                    image=self.tilepalettetkimg)

    def redraw(self):
        self.tileimgtkimg = self.tilegrid.draw(2)
        self.tileimg.itemconfig(self.tileimgimage,
                                image = self.tileimgtkimg)

    def clicktileimg(self, event):
        x = math.floor(self.tileimg.canvasx(event.x)/(8*2))
        y = math.floor(self.tileimg.canvasy(event.y)/(8*2))
        self.tilegrid.set(x, y, 0, self.loadergrid.get(), 
                          self.pageflip.value, 0, 0)
        self.redraw()

class TileGrid:
    def __init__(self):
        self.width = 32
        self.height = 32
        self.layers = []
        self.layers.append({})
        self.grids = {}

    def set(self, x, y, l, grid, gp, gx, gy):
        self.layers[l][(x,y)] = (grid, gp, gx, gy)

    def draw(self, zoom):
        photo = tk.PhotoImage(width=8*self.width*zoom,
                              height=8*self.height*zoom)
        for layer in self.layers:
            for loc in layer:
                gset = layer[loc]
                x = loc[0]*zoom*8
                y = loc[1]*zoom*8
                self.get_grid(gset[0]).drawTkSubset(
                        photo, zoom, gset[2], gset[3], 1, 1, x, y,
                        layer == self.layers[0], gset[1])
        return photo
                

    def add_dependency(self, filename, grid):
        self.grids[os.path.basename(filename)] = (filename, grid)

    def get_grid(self, grid):
        return self.grids[grid][1]

    @property
    def dependencies(self):
        return self.grids.keys()

class Flipper(tk.Frame):
    def __init__(self, parent, top=0, onchange=None):
        tk.Frame.__init__(self, parent)
        self.top = top
        self.value = 0
        self.onchange=onchange

        self.createWidgets()

    def createWidgets(self):
        self.label = tk.Label(self, text=self._labeltext())
        self.label.grid(row=0, column=0)
        self.left_button = tk.Button(self, text="<", 
                                     command=lambda: self._onchange(-1))
        self.left_button.grid(row=0, column=1)
        self.right_button = tk.Button(self, text=">", 
                                      command=lambda: self._onchange(+1))
        self.right_button.grid(row=0, column=2)
        self._buttonstate()

    def _labeltext(self):
        return str(self.value+1)+"/"+str(self.top+1)

    def _buttonstate(self):
        if self.value == 0:
            self.left_button.config(state=tk.DISABLED)
        else:
            self.left_button.config(state=tk.NORMAL)
        
        if self.value == self.top:
            self.right_button.config(state=tk.DISABLED)
        else:
            self.right_button.config(state=tk.NORMAL)

    def reset(self):
        self._buttonstate()
        self.label.config(text=self._labeltext())

    def _onchange(self, delta):
        self.value = self.value + delta
        if self.onchange is not None:
            self.onchange()
        self.reset()

root = tk.Tk()
app = Application(master=root)
app.mainloop()
