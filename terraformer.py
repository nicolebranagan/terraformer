import tkinter as tk
import tkinter.ttk as ttk
import math

import palette
import tool
from pixelgrid import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.selectedx = 0
        self.selectedy = 0
        self.selecting = False
        self.currentcolor = 0
        self.clipboard = None

        self.currenttool = tool.Pencil(False)
        self.pack()
        self.configure()
        self.createWidgets()
        self.newFile()

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
        filemenu.add_command(label="Open")
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
        self.imagecanvas.bind("<Button-3>", self.rclickimagecanvas)
        self.imagecanvas.bind("<B3-Motion>", self.rmotionimagecanvas)

        # Create canvas for editing
        self.editcanvas = tk.Canvas(self, width=512, height=512)
        self.editcanvas.grid(row=1, column=2)
        self.editcanvasimage = self.editcanvas.create_image(
                0,0,anchor=tk.NW)
        self.editcanvas.bind("<Button-1>", self.clickeditcanvas)
        self.editcanvas.bind("<B1-Motion>", self.clickeditcanvas)
        self.editcanvas.bind("<Button-3>", self.rclickeditcanvas)
        
        # Create editing commands
        toolbox = tk.Frame(self)
        toolbox.grid(row=1, column=3)
        pencilbutton = tk.Button(
                toolbox, text="Pencil", 
                command=lambda:self.changetool(tool.Pencil(False)))
        pencilbutton.pack()
        pencilbutton = tk.Button(
                toolbox, text="Alt. P", 
                command=lambda:self.changetool(tool.Pencil(True)))
        pencilbutton.pack()
        
        # Create palette
        self.palettecanvas = tk.Canvas(self, width=512, height=32)
        self.palettecanvas.grid(row=2, column=2)
        self.paletteimage = self.palettecanvas.create_image(
                0, 0, anchor=tk.NW)
        self.paletteselect = self.palettecanvas.create_rectangle(
                1, 1, 32, 32, outline="red")
        self.palettecanvas.bind("<Button-1>", self.clickpalettecanvas)

    def newFile(self):
        # Create new photoimage
        self.pixelgrid = PixelGrid(palette.ega)
        tool.initialize(self.pixelgrid, self.quickdraw, self.redraw)
        self.drawpalette()
        self.image = self.pixelgrid.getTkImage(self.basezoom)
        self.imagecanvas.itemconfig(self.imagecanvasimage, image=self.image)
        self.reselecttile(self.selectedx, self.selectedy)

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
        if not self.selecting:
            self.editimage = self.pixelgrid.getTkSubset(
                    self.basezoom * (256 // (8*self.multiple)),
                    self.selectedx, self.selectedy, 
                    self.multiple)
            self.editcanvas.itemconfig(self.editcanvasimage, 
                                       image=self.editimage)

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
        self.currenttool = tool

root = tk.Tk()
app = Application(master=root)
app.mainloop()
