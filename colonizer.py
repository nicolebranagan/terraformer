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

        self.grids = {}

        self.createWidgets()

    def createWidgets(self):
        # Create menu
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)

        # Create loading buttons
        loadframe = tk.Frame(self)
        loadframe.grid(row=0, column=0)
        openbutton = tk.Button(loadframe, text="Open", command=self.open)
        openbutton.grid(row=0, column=0)
        self.loadergrid = tk.StringVar()
        self.loadergrid.trace("w", self.changegrid)
        self.loader = tk.OptionMenu(
                loadframe, self.loadergrid, "Nothing loaded", "2", "134")
        self.loader.grid(row=0, column=1)

        # Create panels
        self.tilepalette = tk.Canvas(self, width=512, height=512)
        self.tilepalette.grid(row=1, column=0)
        self.tilepaletteimage = self.tilepalette.create_image(
                0, 0, anchor=tk.NW)
        
        self.imgpalette = tk.Canvas(self, width=512, height=512)
        self.imgpalette.grid(row=1, column=1)
        self.imgpaletteimage = self.imgpalette.create_image(
                0, 0, anchor=tk.NW)

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
                self.grids[name] = pixelgrid
                self.resetgrids()

    def changegrid(self, *args):
        self.currentgrid = self.grids[self.loadergrid.get()]
        self.tilepalettetkimg = self.currentgrid.getTkImage(2)
        self.tilepalette.itemconfig(self.tilepaletteimage, 
                                    image=self.tilepalettetkimg)

    def resetgrids(self):
        self.loader["menu"].delete(0, "end")
        for key in self.grids.keys():
            self.loader["menu"].add_command(label=key, command=tk._setit(
                        self.loadergrid, key))


root = tk.Tk()
app = Application(master=root)
app.mainloop()
