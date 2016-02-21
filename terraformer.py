#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import messagebox
import math
import json
import time
import os

import palette
import tool
from pixelgrid import *
import importer

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.selectedx = 0
        self.selectedy = 0
        self.selecting = False
        self.midstep = False
        self.clipboard = None

        self.currenttool = tool.Pencil(False)
        self.pack()
        self.configure()
        self.createWidgets()
        self.new()
        
        self.config = {
            "lastdir" : "./"}
        
        try:
            with open("./config.json", "r") as fileo:
                self.config = json.load(fileo)
        except IOError:
            pass # Just use default

    def configure(self):
        self.basezoom = 2
        self.multiple = 1

    def createWidgets(self):
        self.master.title("Terraformer")
        
        self.master.bind("<Delete>", self.delete)
        self.master.bind("<Control-x>", self.cut)
        self.master.bind("<Control-c>", self.copy)
        self.master.bind("<Control-v>", self.paste)
        self.master.bind("<Control-z>", tool.undo)
        self.master.bind("<Control-s>", self.save)
        
        self.master.bind("<Left>", lambda x: self.reselecttile(
                    self.selectedx-self.multiple, self.selectedy))
        self.master.bind("<Right>", lambda x: self.reselecttile(
                    self.selectedx+self.multiple, self.selectedy))
        self.master.bind("<Up>", lambda x: self.reselecttile(
                    self.selectedx, self.selectedy-self.multiple))
        self.master.bind("<Down>", lambda x: self.reselecttile(
                    self.selectedx, self.selectedy+self.multiple))

        # Create a menu
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="New File", command=self.new)
        filemenu.add_separator()
        filemenu.add_command(label="Open Terraformer File", command=self.open)
        filemenu.add_separator()
        filemenu.add_command(label="Save Terraformer File", command=self.save)
        filemenu.add_command(label="Save As..", command=self.saveas)
        filemenu.add_separator()
        filemenu.add_command(label="Import image", command=self.imports)
        filemenu.add_separator()
        filemenu.add_command(label="Export image to PNG", command=self.export)
        filemenu.add_command(label="Export selection to PNG", 
                command=self.exportselection)
        exportmenu = tk.Menu(filemenu)
        exportmenu.add_command(label="8x8", 
                               command=lambda: self.exportstrip(1))
        exportmenu.add_command(label="16x16", 
                               command=lambda: self.exportstrip(2))
        exportmenu.add_command(label="24x24", 
                               command=lambda: self.exportstrip(3))
        exportmenu.add_command(label="32x32", 
                               command=lambda: self.exportstrip(4))
        filemenu.add_cascade(label="Export image as strip...", 
                             menu=exportmenu)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=exit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        editmenu = tk.Menu(menubar)
        editmenu.add_command(label="Undo", command=tool.undo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut)
        editmenu.add_command(label="Copy", command=self.copy)
        editmenu.add_command(label="Paste", command=self.paste)
        editmenu.add_command(label="Clear clipboard", 
                             command=self.clearclipboard)
        menubar.add_cascade(label="Edit", menu=editmenu)

        palettemenu = tk.Menu(menubar)
        palette1menu = tk.Menu(palettemenu)
        palette1menu.add_command(
                label="EGA",
                command=lambda: self.setpalette(palette.ega))
        palette1menu.add_command(
                label="Windows 16-color",
                command=lambda: self.setpalette(palette.win16))
        palettemenu.add_cascade(label="Predefined palettes", 
                                menu=palette1menu)
        palette2menu = tk.Menu(palettemenu)
        palette2menu.add_command(
                label="Genesis",
                command=lambda: self.constrainpalette(
                    palette.Constraint.Genesis)) 
        palettemenu.add_cascade(label="Constrain palette",
                                menu=palette2menu)
        palettemenu.add_command(
                label="Clear palette",
                command=lambda: self.setpalette(palette.none))
        menubar.add_cascade(label="Palette", menu=palettemenu)

        debugmenu = tk.Menu(menubar)
        debugmenu.add_command(label="Redraw", command=self.redraw)
        menubar.add_cascade(label="Debug", menu=debugmenu)
        
        # Shifters
        shiftframe = tk.Frame(self)
        shiftframe.grid(row=0, column=0)
        hflipbutton = tk.Button(
                shiftframe, text="H. Flip", 
                command=lambda:tool.LinearFunc(
                    -1,0,1,0,1,0).step1(
                    self.getCurrentSelection()))
        hflipbutton.grid(row=0, column=0)
        vflipbutton = tk.Button(
                shiftframe, text="V. Flip", 
                command=lambda:tool.LinearFunc(
                    1,0,0,0,-1,1).step1(
                    self.getCurrentSelection()))
        vflipbutton.grid(row=0, column=1)
        rotcwbutton = tk.Button(
                shiftframe, text="CW", 
                command=lambda:tool.LinearFunc(
                    0,-1,1,1,0,0).step1(self.getCurrentSelection()))
        rotcwbutton.grid(row=0, column=2)
        rotccwbutton = tk.Button(
                shiftframe, text="CCW", 
                command=lambda:tool.LinearFunc(
                    0,1,0,-1,0,1).step1(self.getCurrentSelection()))
        rotccwbutton.grid(row=0, column=3)
        shiftupbutton = tk.Button(
                shiftframe, text="^", 
                command=lambda:tool.Shifter(0,-1).step1(
                    self.getCurrentSelection()))
        shiftupbutton.grid(row=0, column=10)
        shiftdownbutton = tk.Button(
                shiftframe, text="v", 
                command=lambda:tool.Shifter(0,1).step1(
                    self.getCurrentSelection()))
        shiftdownbutton.grid(row=0, column=11)
        shiftleftbutton = tk.Button(
                shiftframe, text="<", 
                command=lambda:tool.Shifter(-1,0).step1(
                    self.getCurrentSelection()))
        shiftleftbutton.grid(row=0, column=12)
        shiftrightbutton = tk.Button(
                shiftframe, text=">", 
                command=lambda:tool.Shifter(1,0).step1(
                    self.getCurrentSelection()))
        shiftrightbutton.grid(row=0, column=13)
        

        # Create canvas for larger view
        self.imagecanvas = tk.Canvas(self, width=512, height=512)
        self.imagecanvas.grid(row=1, column=0)
        self.imagecanvasimage = self.imagecanvas.create_image(
                0,0,anchor=tk.NW)
        self.imagecanvasselection = self.imagecanvas.create_rectangle(
                1, 1, self.multiple * self.basezoom * 8, 
                self.multiple * self.basezoom * 8,
                outline="grey")
        self.imagecanvas.bind("<Button-1>", self.clickimagecanvas)
        self.imagecanvas.bind("<Button-3>", self.rclickimagecanvas)
        self.imagecanvas.bind("<B3-Motion>", self.rmotionimagecanvas)

        # Create canvas for editing
        self.editcanvas = tk.Canvas(self, width=512, height=512)
        self.editcanvas.grid(row=1, column=2)
        self.editcanvasimage = self.editcanvas.create_image(
                0,0,anchor=tk.NW)
        self.editcanvas.bind("<Button-1>", self.clickeditcanvas)
        self.editcanvas.bind("<B1-Motion>", self.motioneditcanvas)
        self.editcanvas.bind("<ButtonRelease-1>", self.releaseeditcanvas)
        self.editcanvas.bind("<Button-3>", self.rclickeditcanvas)
        
        # Create editing commands
        toolbox = tk.Frame(self)
        toolbox.grid(row=1, column=3, sticky=tk.N)
        self.toolboximages = [tk.PhotoImage(file="./images/pencil.gif"),
                              tk.PhotoImage(file="./images/apencil.gif"),
                              tk.PhotoImage(file="./images/line.gif"),
                              tk.PhotoImage(file="./images/rect.gif"),
                              tk.PhotoImage(file="./images/arect.gif"),
                              tk.PhotoImage(file="./images/box.gif"),
                              tk.PhotoImage(file="./images/circ.gif"),
                              tk.PhotoImage(file="./images/bcirc.gif"),
                              tk.PhotoImage(file="./images/fill.gif")]
        pencilbutton = tk.Button(
            toolbox, image=self.toolboximages[0], width=24, height=24, 
            command=lambda:self.changetool(tool.Pencil(False)))
        pencilbutton.pack()
        pencilbutton = tk.Button(
            toolbox, image=self.toolboximages[1], width=24, height=24,  
            command=lambda:self.changetool(tool.Pencil(True)))
        pencilbutton.pack()
        linebutton = tk.Button(
            toolbox, image=self.toolboximages[2], width=24, height=24, 
            command=lambda:self.changetool(tool.Line()))
        linebutton.pack()
        rectbutton = tk.Button(
            toolbox, image=self.toolboximages[3], width=24, height=24,  
            command=lambda:self.changetool(tool.Rectangle(False, True)))
        rectbutton.pack()
        arectbutton = tk.Button(
            toolbox, image=self.toolboximages[4], width=24, height=24,  
              command=lambda:self.changetool(tool.Rectangle(True, True)))
        arectbutton.pack()
        boxbutton = tk.Button(
            toolbox, image=self.toolboximages[5], width=24, height=24,  
            command=lambda:self.changetool(tool.Rectangle(False, False)))
        boxbutton.pack()
        circbutton = tk.Button(
            toolbox, image=self.toolboximages[6], width=24, height=24,  
            command=lambda:self.changetool(tool.Circle()))
        circbutton.pack()
        fcircbutton = tk.Button(
            toolbox, image=self.toolboximages[7], width=24, height=24,  
            command=lambda:self.changetool(tool.FilledCircle()))
        fcircbutton.pack()
        fillbutton = tk.Button(
            toolbox, image=self.toolboximages[8], width=24, height=24,  
            command=lambda:self.changetool(tool.Fill()))
        fillbutton.pack()
        
        # Create lower panel
        lowerpanel1 = tk.Frame(self)
        lowerpanel1.grid(row=2, column=0)
        self.multiplescale = ttk.Scale(lowerpanel1, from_=1.0, to=8.0,
                                      orient=tk.HORIZONTAL,
                                      command=self.resetscale)
        self.multiplescale.grid(row=0, column=0, sticky=tk.W)
        tk.Frame(lowerpanel1, width=256).grid(row=0, column=1)
        lowerpanel1_1 = tk.Frame(lowerpanel1)
        lowerpanel1_1.grid(row=0, column=2, sticky=tk.E)
        self.pagelabel = tk.Label(lowerpanel1_1, text="1/1")
        self.pagelabel.grid(row=0, column=0)
        self.prevpagebutton = tk.Button(lowerpanel1_1, text="<",
                                        state=tk.DISABLED,
                                        command = lambda: self.paginate(-1))
        self.prevpagebutton.grid(row=0, column=1)
        nextpagebutton = tk.Button(lowerpanel1_1, text=">",
                                   command = lambda: self.paginate(1))
        nextpagebutton.grid(row=0,column=2)
        self.delpagebutton = tk.Button(lowerpanel1_1, text="X",
                                        state=tk.DISABLED,
                                        command=self.deletepage)
        self.delpagebutton.grid(row=0, column=3)
        
        # Create palette
        self.palettecanvas = tk.Canvas(self, width=512, height=32)
        self.palettecanvas.grid(row=2, column=2)
        self.paletteimage = self.palettecanvas.create_image(
                0, 0, anchor=tk.NW)
        self.paletteselect = self.palettecanvas.create_rectangle(
                1, 1, 32, 32, outline="red")
        self.palettecanvas.bind("<Button-1>", self.clickpalettecanvas)
        self.palettecanvas.bind("<Button-3>", self.rclickpalettecanvas)
        self.palettecanvas.bind("<Double-Button-1>", self.dclickpalettecanvas)

        # Image grabber
        self.imagegrab = tk.Canvas(self, width=512, height=64)
        self.imagegrab.grid(row=3,column=2)
        self.imagegrabimg = self.imagegrab.create_image(0, 0, anchor=tk.NW)
        self.imagegrabtkimg = tk.PhotoImage(file="./images/nes.gif")
        self.imagegrab.itemconfig(self.imagegrabimg, image=self.imagegrabtkimg)
        self.imagegrab.bind("<Button-1>", self.clickimagegrab)

        # Create status bar
        self.statusbar = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  text="Welcome to Terraformer")
        self.statusbar.grid(row=4, column=0, columnspan=4, sticky=tk.W+tk.E)

    def new(self):
        # Create new photoimage
        self.pixelgrid = PixelGrid(palette.ega[:])
        tool.initialize(self.pixelgrid, self.quickdraw, self.redraw)
        self.reselecttile(self.selectedx, self.selectedy)
        self.multiplescale.set(2.0)
        self.currentpage = 0
        self.selecting = False
        self.midstep = False
        self.prevpagebutton.config(state=tk.DISABLED)
        self.pagelabel.config(text="1/1")
        self.currentfilename = ""
        self.selectcolor(0)
        self.drawpalette()
        self.redraw()

    def drawpalette(self):
        self.palette = tk.PhotoImage(width=512, height=32)
        i = 0
        for c in self.pixelgrid.palette:
            self.palette.put("#%02x%02x%02x" % c,
                             to=(i*32,0,(i+1)*32,32))
            i = i+1
        self.palettecanvas.itemconfig(self.paletteimage, image=self.palette)

    def resetscale(self, event):
        test = math.floor(self.multiplescale.get())
        if test == 3:
            if (self.multiple > test):
                self.multiple = 2
            else:
                self.multiple = 4
        elif test == 5:
            self.multiple = 4
        elif test == 6:
            if (self.multiple > test):
                self.multiple = 4
            else:
                self.multiple = 8
        elif test == 7:
            self.multiple = 8
        else:
            self.multiple = test

        self.reselecttile(self.selectedx, self.selectedy)

    def clickimagecanvas(self, event):
        if (self.selecting):
            self.selecting = False
            self.imagecanvas.itemconfig(self.imagecanvasselection, outline="grey")

        x = math.floor(
                self.imagecanvas.canvasx(event.x) / 
                (self.basezoom * 8))
        y = math.floor(
                self.imagecanvas.canvasy(event.y) / 
                (self.basezoom * 8))
        self.reselecttile(x, y)

    def rclickimagecanvas(self, event):
        self.selecting = True
        self.imagecanvas.itemconfig(self.imagecanvasselection, outline="cyan")
        self.selection = [
            math.floor(self.imagecanvas.canvasx(event.x) / 
                       (self.basezoom * 8)),
            math.floor(self.imagecanvas.canvasy(event.y) / 
                       (self.basezoom * 8)),
            math.floor(self.imagecanvas.canvasx(event.x) / 
                       (self.basezoom * 8)) + 1,
            math.floor(self.imagecanvas.canvasy(event.y) / 
                       (self.basezoom * 8)) + 1]
        self.imagecanvas.coords(self.imagecanvasselection, 
                                self.selection[0] * self.basezoom * 8,
                                self.selection[1] * self.basezoom * 8,
                                self.selection[2] * self.basezoom * 8,
                                self.selection[3] * self.basezoom * 8)

        if self.clipboard is None:
            self.editimage = tk.PhotoImage()
        else:
            self.editimage = self.clipboard.getTkImage(self.basezoom)
        self.editcanvas.itemconfig(self.editcanvasimage, 
                                   image=self.editimage)

    def rmotionimagecanvas(self, event):
        newx = math.floor(self.imagecanvas.canvasx(event.x) / 
                          (self.basezoom * 8))
        newy = math.floor(self.imagecanvas.canvasy(event.y) /
                          (self.basezoom * 8))
        
        # Stay in the grid
        newx = max(min(32, newx), 0)
        newy = max(min(32, newy), 0)

        if (newx != self.selection[0]):
            self.selection[2] = newx
        if (newy != self.selection[1]):
            self.selection[3] = newy

        self.imagecanvas.coords(
                self.imagecanvasselection,
                min(self.selection[0], self.selection[2])*
                self.basezoom*8,
                min(self.selection[1], self.selection[3])*
                self.basezoom*8,
                max(self.selection[0], self.selection[2])*
                self.basezoom*8,
                max(self.selection[1], self.selection[3])*
                self.basezoom*8)

    def reselecttile(self, x, y):
        self.midstep = False
        if (self.selecting):
            self.selecting = False
            self.imagecanvas.itemconfig(self.imagecanvasselection, outline="grey")
        
        if (x + self.multiple > 32):
            x = 32 - self.multiple
        if (y + self.multiple > 32):
            y = 32 - self.multiple
        if (x < 0):
            x = 0
        if (y < 0):
            y = 0

        self.selectedx = x
        self.selectedy = y

        newx = self.selectedx * self.basezoom * 8
        newy = self.selectedy * self.basezoom * 8
        self.imagecanvas.coords(self.imagecanvasselection, newx, newy,
                                newx + self.multiple * self.basezoom * 8,
                                newy + self.multiple * self.basezoom * 8)

        self.editimage = self.pixelgrid.getTkSubset(
                self.basezoom * (256 // (8*self.multiple)),
                self.selectedx, self.selectedy, 
                self.multiple)
        self.editcanvas.itemconfig(self.editcanvasimage, 
                                   image=self.editimage)

    def clickeditcanvas(self, event):
        if (self.selecting): return

        x = math.floor(self.editcanvas.canvasx(event.x) // (self.basezoom *
            256 // (8*self.multiple))) 
        y = math.floor(self.editcanvas.canvasy(event.y) // (self.basezoom *
            256 // (8*self.multiple)))

        if (x < 0 or y < 0 or x >= self.multiple * 8 or y >= self.multiple * 8):
            return
        
        self.currenttool.step1(self.selectedx, self.selectedy, 
                               x, y, self.currentcolor)
        if self.currenttool.twostep:
            self.midstep = True

    def motioneditcanvas(self, event):
        if self.midstep:
            x = math.floor(self.editcanvas.canvasx(event.x) // (self.basezoom *
                256 // (8*self.multiple))) 
            y = math.floor(self.editcanvas.canvasy(event.y) // (self.basezoom *
                256 // (8*self.multiple)))
            self.currenttool.move(self.selectedx, self.selectedy, 
                                  x, y, self.currentcolor)
        else:
            self.clickeditcanvas(event)
    
    def releaseeditcanvas(self, event):
        if not self.midstep: return

        x = math.floor(self.editcanvas.canvasx(event.x) // (self.basezoom *
            256 // (8*self.multiple))) 
        y = math.floor(self.editcanvas.canvasy(event.y) // (self.basezoom *
            256 // (8*self.multiple)))
        
        self.currenttool.step2(self.selectedx, self.selectedy, 
                               x, y, self.currentcolor)
        self.midstep = False
        

    def rclickeditcanvas(self, event):
        if (self.selecting): return
        
        x = math.floor(self.editcanvas.canvasx(event.x) // (self.basezoom *
            256 // (8*self.multiple))) 
        y = math.floor(self.editcanvas.canvasy(event.y) // (self.basezoom *
            256 // (8*self.multiple)))

        self.selectcolor(self.pixelgrid.get(self.selectedx * 8 + x,
                         self.selectedy * 8 + y))

    def clickpalettecanvas(self, event):
        i = math.floor(self.palettecanvas.canvasx(event.x) // 32)
        if i < len(self.pixelgrid.palette):
            self.selectcolor(i)

    def rclickpalettecanvas(self, event):
        i = math.floor(self.palettecanvas.canvasx(event.x) // 32)
        if i < len(self.pixelgrid.palette):
            tool.undoblock(self.getCurrentSelection())
            self.pixelgrid.flipColors(self.currentcolor, i,
                                      self.getCurrentSelection())
            self.redraw()

    def dclickpalettecanvas(self, event):
        i = math.floor(self.palettecanvas.canvasx(event.x) // 32)
        if i < len(self.pixelgrid.palette):
            color=colorchooser.askcolor(
                    initialcolor=self.pixelgrid.palette[i])
            if color[0] is None:
                return
            tool.undopalette()
            newcolor = (int(color[0][0]),int(color[0][1]),int(color[0][2]))
            self.pixelgrid.palette[i] = newcolor
            self.drawpalette()
            self.redraw()
    
    def clickimagegrab(self, event):
        x = int(self.imagegrab.canvasx(event.x))
        y = int(self.imagegrab.canvasy(event.y))
        tool.undopalette()
        newcolor = self.imagegrabtkimg.get(x,y)
        self.pixelgrid.palette[self.currentcolor] = newcolor
        self.redraw(True, True, True)

    def selectcolor(self, i):
        self.midstep = False
        self.currentcolor = i
        self.palettecanvas.coords(self.paletteselect, i*32, 1, (i+1)*32, 32)

    def setpalette(self, p):
        newp = p[:] # Keep original palette unaltered
        tool.undopalette()
        self.pixelgrid.palette = newp
        self.currentcolor = 0
        self.drawpalette()
        self.redraw()

    def constrainpalette(self, c):
        tool.undopalette()
        palette.constrain(self.pixelgrid.palette, c)
        self.drawpalette()
        self.redraw()

    def quickdraw(self, x, y, v):
        if x < 0 or y < 0:
            return
        
        zoom = self.basezoom * 256 // (8*self.multiple)
        self.editimage.put("#%02x%02x%02x" % self.pixelgrid.palette[v],
                           to=(x*zoom, y*zoom, x*zoom + zoom, y*zoom + zoom))
        
        x = x + 8*self.selectedx
        y = y + 8*self.selectedy
        zoom = self.basezoom
        
        color = self.pixelgrid.palette[v]
        
        self.image.put("#%02x%02x%02x" % color,
                       to=(x*zoom, y*zoom, x*zoom + zoom, y*zoom + zoom))
        
    def redraw(self, image=True, canvas=True, palette=False):
        if image:
            self.image = self.pixelgrid.getTkImage(self.basezoom)
            self.imagecanvas.itemconfig(self.imagecanvasimage, image=self.image)
        if canvas and not self.selecting:
            self.editimage = self.pixelgrid.getTkSubset(
                    self.basezoom * (256 // (8*self.multiple)),
                    self.selectedx, self.selectedy, 
                    self.multiple)
            self.editcanvas.itemconfig(self.editcanvasimage, 
                                       image=self.editimage)
        if palette:
            self.drawpalette()

    def delete(self, event=None):
        select = self.getCurrentSelection()
        tool.Delete().step1(select[0], select[1], select[2], select[3], 0)
        self.redraw()

    def cut (self, event=None): 
        self.copy()
        self.delete()

    def copy(self, event=None):
        self.clipboard = PixelSubset(
                self.pixelgrid,
                self.getCurrentSelection())
        self.editimage = self.clipboard.getTkImage(self.basezoom)
        self.editcanvas.itemconfig(self.editcanvasimage, 
                                   image=self.editimage)

    def paste(self, event=None):
        if self.clipboard is None:
            return

        if (self.selecting):
            x = min(self.selection[0], self.selection[2])
            y = min(self.selection[1], self.selection[3])
        else:
            x = self.selectedx
            y = self.selectedy
        
        currentsel = self.getCurrentSelection()
        tool.undoblock([currentsel[0],
                        currentsel[1],
                        currentsel[0]+self.clipboard.width,
                        currentsel[1]+self.clipboard.height])
        self.pixelgrid.mergeSubset(self.clipboard, x, y)
        self.redraw()
    
    def clearclipboard(self):
        self.clipboard = None

    def getCurrentSelection(self):
        output = [0,0,0,0]
        if (self.selecting):
            output[0] = min(self.selection[0], self.selection[2])
            output[2] = max(self.selection[0], self.selection[2])
            output[1] = min(self.selection[1], self.selection[3])
            output[3] = max(self.selection[1], self.selection[3])
        else:
            # Return the current tile
            output[0] = self.selectedx
            output[1] = self.selectedy
            output[2] = self.selectedx + self.multiple
            output[3] = self.selectedy + self.multiple
        return output

    def changetool(self, tool):
        self.midstep = False
        self.currenttool = tool

    def open(self):
        filen = filedialog.askopenfilename(
                filetypes=(("Terraformer images", "*.terra"),
                           ("All files", "*")),
                title="Open paletted image",
                initialdir=self.config["lastdir"])
        if filen != () and filen != "":
            with open(filen, "r") as fileo:
                self.pixelgrid.load(json.load(fileo))
            self.drawpalette()
            self.redraw()
                
            self.currentpage = 0
            self.prevpagebutton.config(state=tk.DISABLED)
            self.pagelabel.config(
                text="{0}/{1}".format(self.currentpage+1,
                                      self.pixelgrid.pages))
            self.config["lastdir"] = os.path.dirname(filen)
            self.currentfilename = os.path.basename(filen) 
            try:
                with open("./config.json", "w") as fileo:
                    json.dump(self.config, fileo)
            except IOError:
                pass # Not a big deal
            self.statusbar.config(text=(
                        "Opened file " + self.currentfilename + " at " +
                        time.strftime("%I:%M %p", time.localtime())))

    def save(self, event=None):
        if self.currentfilename == "":
            self.saveas()
        else:
            self.savefile(os.path.join(
                        self.config["lastdir"],
                        self.currentfilename))

    def saveas(self):
        name = "image.terra"
        if self.currentfilename != "":
            name = self.currentfilename

        filen = filedialog.asksaveasfilename(
                defaultextension=".terra",
                initialfile=name,
                initialdir=self.config["lastdir"],
                filetypes=(("Terraformer images", "*.terra"),
                           ("All files", "*")),
                title="Save paletted image to file")
        if filen != () and filen != "":
            with open(filen, "w") as fileo:
                self.savefile(filen)

    def savefile(self, name):
        grid = self.pixelgrid.dump()
        with open(name, "w") as fileo:
            json.dump(grid, fileo)
        self.config["lastdir"] = os.path.dirname(name)
        self.currentfilename = os.path.basename(name)
        self.statusbar.config(text=(
                    "Saved file " + self.currentfilename + " at " +
                    time.strftime("%I:%M %p", time.localtime())))
    
    def export(self):
        filen = filedialog.asksaveasfilename(
                defaultextension=".png",
                title="Export to file")
        if filen != ():
            self.pixelgrid.getTkImage(1).write(filen)

    def exportselection(self):
        filen = filedialog.asksaveasfilename(
                defaultextension=".png",
                title="Export to file")
        if filen != ():
            PixelSubset(
                self.pixelgrid,
                self.getCurrentSelection()).getTkImage(1).write(filen)
    
    def imports(self):
        filen = filedialog.askopenfilename(
                defaultextension=".png",
                title="Import file")
        if filen != ():
            self.statusbar.config(text="Please wait")
            self.pixelgrid = importer.importpixelgrid(filen)
            self.statusbar.config(text="Imported file successfully.")
            self.redraw(True, True, True)
            

    def exportstrip(self, height):
        filen = filedialog.asksaveasfilename(
                defaultextension=".png",
                title="Export strip to file")
        if filen != ():
            self.pixelgrid.getTkStrip(height).write(filen)
    
    def paginate(self, by):
        self.currentpage = self.currentpage + by
        self.pixelgrid.changepage(self.currentpage)
        if self.currentpage > 0:
            self.prevpagebutton.config(state=tk.NORMAL)
        else:
            self.prevpagebutton.config(state=tk.DISABLED)
        self.pagelabel.config(
            text="{0}/{1}".format(self.currentpage+1,
                                  self.pixelgrid.pages))
        if self.currentpage > 0 and (self.currentpage+1 == 
                                     self.pixelgrid.pages):
            self.delpagebutton.config(state=tk.NORMAL)
        else:
            self.delpagebutton.config(state=tk.DISABLED)
        
        self.redraw()

    def deletepage(self):
        if not self.pixelgrid.ispageclear(self.currentpage):
            result = messagebox.askyesno(
                    "Delete page",
                    ("Okay to delete page?\n"
                     "All information will be lost.\n"
                     "This action can not be undone."),
                    default = messagebox.NO)
            if not result:
                return
        self.pixelgrid.dellastpage()
        self.paginate(-1)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
