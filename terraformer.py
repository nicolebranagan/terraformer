import tkinter as tk
import tkinter.ttk as ttk
import math

from pixelgrid import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
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

        # Create zoom
        self.multiplescale = tk.Scale(self, from_=1.0, to=8.0,
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

    def newFile(self):
        # Create new photoimage
        self.pixelgrid = PixelGrid([(0,0,0),(255,255,255)])
        self.pixelgrid.set(45,45,1)
        self.image = self.pixelgrid.getTkImage(self.basezoom)
        self.imagecanvas.itemconfig(self.imagecanvasimage, image=self.image)

    def resetscale(self, event):
        self.multiple=self.multiplescale.get()

    def clickimagecanvas(self, event):
        # Click on imagecanvas
        newx = self.multiple * self.basezoom * 8 * math.floor(
                self.imagecanvas.canvasx(event.x) / 
                (self.basezoom * self.multiple * 8))
        newy = self.multiple * self.basezoom * 8 * math.floor(
                self.imagecanvas.canvasy(event.y) / 
                (self.basezoom * self.multiple * 8))
        self.imagecanvas.coords(self.imagecanvasselection, newx, newy,
                                newx + self.multiple * self.basezoom * 8,
                                newy + self.multiple * self.basezoom * 8)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
