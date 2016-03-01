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
        self.selection = (0, 0, 1, 1)
        self.createWidgets()
        self.currentlayer = 0
        
        self.config = {
            "lastdir" : "./"}
        
        try:
            with open("./config.json", "r") as fileo:
                self.config = json.load(fileo)
        except IOError:
            pass # Just use default

        self.redraw()

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
        self.layerflip = Flipper(self, onchange=self.changelayer, top=8)
        self.layerflip.grid(row=0, column=2, sticky=tk.E)

        # Create panels
        self.tilepalette = tk.Canvas(self, width=512, height=512)
        self.tilepalette.grid(row=1, column=0, columnspan=2)
        self.tilepaletteimage = self.tilepalette.create_image(
                0, 0, anchor=tk.NW)
        self.tilepaletteselection = self.tilepalette.create_rectangle(
                1, 1, 16, 16, outline="grey")
        self.tilepalette.bind("<Button-1>", self.clicktilepalette)
        self.tilepalette.bind("<B1-Motion>", self.motiontilepalette)

        self.tileimg = tk.Canvas(self, width=512, height=512)
        self.tileimg.grid(row=1, column=2)
        self.tileimgimage = self.tileimg.create_image(
                0, 0, anchor=tk.NW)
        self.tileimg.bind("<Button-1>", self.clicktileimg)
        self.tileimg.bind("<B1-Motion>", self.motiontileimg)

    def open(self):
        filen = filedialog.askopenfilename(
                filetypes=(("Terraformer images", "*.terra"),
                           ("All files", "*")),
                title="Open paletted image",
                initialdir=self.config["lastdir"])
        if filen != () and filen != "":
            with open(filen, "r") as fileo:
                pixelgrid = PixelGrid([(0,0,0)])
                pixelgrid.load(json.load(fileo))
                name = os.path.basename(filen)
                self.tilegrid.add_dependency(filen, pixelgrid)
                self.resetgrids()

    def changegrid(self, *args):
        if self.loadergrid.get() == "Nothing loaded":
            return
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

    def changelayer(self):
        self.currentlayer = self.layerflip.value

    def redraw(self):
        self.tileimgtkimg = self.tilegrid.draw(2)
        self.tileimg.itemconfig(self.tileimgimage,
                                image = self.tileimgtkimg)

    def clicktileimg(self, event):
        if (self.loadergrid.get() == "" or
                self.loadergrid.get() == "Nothing loaded"):
            return

        x = math.floor(self.tileimg.canvasx(event.x)/(8*2))
        y = math.floor(self.tileimg.canvasy(event.y)/(8*2))

        self.settileimgarea(x, y)
        self.lastclick = (x, y)
       
    def motiontileimg(self, event):
        if (self.loadergrid.get() == "" or
                self.loadergrid.get() == "Nothing loaded"):
            return

        x = math.floor(self.tileimg.canvasx(event.x)/(8*2))
        y = math.floor(self.tileimg.canvasy(event.y)/(8*2))
        width = abs(self.selection[0] - self.selection[2])
        height = abs(self.selection[1] - self.selection[3])
        
        if ((x - self.lastclick[0]) % width == 0 and
            (y - self.lastclick[1]) % height == 0):
            self.settileimgarea(x,y)

    def settileimgarea(self, x, y):
        selection = (min(self.selection[0], self.selection[2]),
                     min(self.selection[1], self.selection[3]),
                     max(self.selection[0], self.selection[2]),
                     max(self.selection[1], self.selection[3]))
        
        for i in range(0, selection[2]-selection[0]):
            for j in range(0, selection[3]-selection[1]):
                self.tilegrid.set(
                        x + i, y + j, self.currentlayer, 
                        self.loadergrid.get(), 
                        self.pageflip.value, 
                        selection[0] + i, 
                        selection[1] + j)
        self.redraw()

    def clicktilepalette(self, event):
        if (self.loadergrid.get() == "" or
                self.loadergrid.get() == "Nothing loaded"):
            return

        x = math.floor(self.tileimg.canvasx(event.x)/(8*2))
        y = math.floor(self.tileimg.canvasy(event.y)/(8*2))
        self.selection = (x, y, x+1, y+1)
        self.resetselection()
    
    def motiontilepalette(self, event):
        if (self.loadergrid.get() == "" or
                self.loadergrid.get() == "Nothing loaded"):
            return

        x = math.floor(self.tileimg.canvasx(event.x)/(8*2))
        y = math.floor(self.tileimg.canvasy(event.y)/(8*2))
        
        if (x,y) is not (self.selection[0], self.selection[1]):
            self.selection = (self.selection[0],
                              self.selection[1],
                              x,
                              y)
        self.resetselection()
    
    def resetselection(self):
        selection = (min(self.selection[0], self.selection[2]),
                     min(self.selection[1], self.selection[3]),
                     max(self.selection[0], self.selection[2]),
                     max(self.selection[1], self.selection[3]))
        self.tilepalette.coords(self.tilepaletteselection, 
                                selection[0] * 2 * 8,
                                selection[1] * 2 * 8,
                                selection[2] * 2 * 8,
                                selection[3] * 2 * 8)

class TileGrid:
    def __init__(self):
        self.width = 32
        self.height = 32
        self.layers = []
        self.layers.append({})
        self.grids = {}

    def set(self, x, y, l, grid, gp, gx, gy):
        while(len(self.layers) < l+1):
            self.layers.append({})
        self.layers[l][(x,y)] = (grid, gp, gx, gy)

    def draw(self, zoom):
        photo = tk.PhotoImage(width=8*self.width*zoom,
                              height=8*self.height*zoom)
        photo.put("#000000", 
                  to=(0,0,8*self.width*zoom,8*self.height*zoom))
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
