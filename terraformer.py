import tkinter as tk
import tkinter.ttk as ttk
import math

import palette
from pixelgrid import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.selectedx = 0
        self.selectedy = 0
        self.currentcolor = 0

        self.pack()
        self.configure()
        self.createWidgets()
        self.newFile()

    def configure(self):
        self.basezoom = 2
        self.multiple = 1

    def createWidgets(self):
        self.master.title("Terraformer")
        
        # Create a menu
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Open")
        menubar.add_cascade(label="File", menu=filemenu)

        palettemenu = tk.Menu(menubar)
        palettemenu.add_command(
                label="EGA",
                command=lambda: self.setpalette(palette.ega))
        palettemenu.add_command(
                label="Windows 16-color",
                command=lambda: self.setpalette(palette.win16))
        menubar.add_cascade(label="Palette", menu=palettemenu)

        debugmenu = tk.Menu(menubar)
        debugmenu.add_command(label="Redraw", command=self.redraw)
        menubar.add_cascade(label="Debug", menu=debugmenu)
        
        # Create zoom
        self.multiplescale = ttk.Scale(self, from_=1.0, to=8.0,
                                      orient=tk.HORIZONTAL,
                                      command=self.resetscale)
        self.multiplescale.grid(row=0, column=0)

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
        
        # Create canvas for editing
        self.editcanvas = tk.Canvas(self, width=512, height=512)
        self.editcanvas.grid(row=1, column=1)
        self.editcanvasimage = self.editcanvas.create_image(
                0,0,anchor=tk.NW)
        self.editcanvas.bind("<Button-1>", self.clickeditcanvas)
        self.editcanvas.bind("<B1-Motion>", self.clickeditcanvas)
        self.editcanvas.bind("<Button-3>", self.rclickeditcanvas)

        # Create palette
        self.palettecanvas = tk.Canvas(self, width=512, height=32)
        self.palettecanvas.grid(row=2, column=1)
        self.paletteimage = self.palettecanvas.create_image(
                0, 0, anchor=tk.NW)
        self.paletteselect = self.palettecanvas.create_rectangle(
                1, 1, 32, 32, outline="red")
        self.palettecanvas.bind("<Button-1>", self.clickpalettecanvas)

    def newFile(self):
        # Create new photoimage
        self.pixelgrid = PixelGrid(palette.ega)
        self.drawpalette()
        self.image = self.pixelgrid.getTkImage(self.basezoom)
        self.imagecanvas.itemconfig(self.imagecanvasimage, image=self.image)
        self.reselecttile()

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

        self.reselecttile()

    def clickimagecanvas(self, event):
        # Click on imagecanvas
        self.selectedx = math.floor(
                self.imagecanvas.canvasx(event.x) / 
                (self.basezoom * 8))
        self.selectedy = math.floor(
                self.imagecanvas.canvasy(event.y) / 
                (self.basezoom * 8))
        self.reselecttile()

    def reselecttile(self):
        if (self.selectedx + self.multiple > 32):
            self.selectedx = 32 - self.multiple
        if (self.selectedy + self.multiple > 32):
            self.selectedy = 32 - self.multiple
        
        newx = self.selectedx * self.basezoom * 8 + 1
        newy = self.selectedy * self.basezoom * 8 + 1
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
        x = math.floor(self.editcanvas.canvasx(event.x) // (self.basezoom *
            256 // (8*self.multiple))) 
        y = math.floor(self.editcanvas.canvasy(event.y) // (self.basezoom *
            256 // (8*self.multiple)))

        if (x < 0 or y < 0 or x >= self.multiple * 8 or y >= self.multiple * 8):
            return

        self.pixelgrid.set(self.selectedx * 8 + x, self.selectedy * 8 + y, 
                           self.currentcolor)
        self.quickdraw(x, y, self.currentcolor)
    
    def rclickeditcanvas(self, event):
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

    def selectcolor(self, i):
        self.currentcolor = i
        self.palettecanvas.coords(self.paletteselect, i*32, 1, (i+1)*32, 32)

    def setpalette(self, p):
        p = list(p) # Keep original palette unaltered
        self.pixelgrid.palette = p
        self.currentcolor = 0
        self.drawpalette()
        self.redraw()

    def quickdraw(self, x, y, v):
        zoom = self.basezoom * 256 // (8*self.multiple)
        self.editimage.put("#%02x%02x%02x" % self.pixelgrid.palette[v],
                           to=(x*zoom, y*zoom, x*zoom + zoom, y*zoom + zoom))
        
        x = x + 8*self.selectedx
        y = y + 8*self.selectedy
        zoom = self.basezoom
        self.image.put("#%02x%02x%02x" % self.pixelgrid.palette[v],
                       to=(x*zoom, y*zoom, x*zoom + zoom, y*zoom + zoom))
        
    def redraw(self):
        self.image = self.pixelgrid.getTkImage(self.basezoom)
        self.imagecanvas.itemconfig(self.imagecanvasimage, image=self.image)
        self.editimage = self.pixelgrid.getTkSubset(
                self.basezoom * (256 // (8*self.multiple)),
                self.selectedx, self.selectedy, 
                self.multiple)
        self.editcanvas.itemconfig(self.editcanvasimage, 
                                   image=self.editimage)



root = tk.Tk()
app = Application(master=root)
app.mainloop()
