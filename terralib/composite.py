from PIL import Image, ImageTk
import math
import terralib.pixelgrid as pixelgrid
import colorsys

def convert(terraimg):
    tkimg = terraimg.getTkImage(1)
    y = []
    i = []
    q = []
    for i in range(0, tkimg.width()):
        for j in range(0, tkimg.height()):
            color = tkimg.get(i, j)]
            yiq = colorsys.rgb_to_yiq(color[0], color[1], color[2])
            y.append(yiq[0])
            i.append(yiq[1])
            q.append(yiq[2])
