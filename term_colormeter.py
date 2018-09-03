# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImagStat
import json
import sys

ANSI_COLORS = [(0,0,0),(153,0,0),(0,166,0),(153,153,0),(0,0,178),(178,0,178),(0,166,178),(191,191,191)]
ANSI_FG_CODES = [30,31,32,33,34,35,36,37]
ANSI_BG_CODES = [40,41,42,43,44,45,46,47]
ANSI_NAMES = ['black','red','green','yellow','blue','magenta','cyan','white']
CHARS = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
FONT = "Monaco"

def color_text(s,fg,bg):
    format = ';'.join([0, str(fg), str(bg)])
    return '\x1b[%sm%s\x1b[0m' % (format)

def render(s,fg,bg,font=FONT):
    fnt = ImageFont.truetype(font, 24)
    fgcol = ANSI_COLORS[ANSI_FG_CODES.index(fg)]
    bgcol = ANSI_COLORS[ANSI_BG_CODES.index(bg)]
    im = Image.new("RGB",(14,28),bgcol)
    dr = ImageDraw.Draw(im)
    dr.text((0,-2), s, font=fnt, fill=fgcol)
    return im

def test_render(fg,bg,font=FONT):
    im = Image.new("RGB",(224,224*2))
    for i in range(0,255):
        x,y = (i*14)%im.size[0],28*((i*14)//im.size[0])
        im.paste(render(chr(i),fg,bg,font), (x,y))
    return im

def avarage(im):
    return ImageStat.Stat(im).mean

def estimate(s,fg,bg,font="Monaco"):
    im = render(s,fg,bg,font=font)
    return avarage(im)

def generate_color_map():
    table = {}
    for fg in ANSI_FG_CODES:
        for bg in ANSI_BG_CODES:
            for ch in CHARS:
                config = (ch,fg,bg)
                col = estimate(*config)
                table[col] = config
    return table

if __name__ == "__main__":
    FONT = sys.argv[1]
    cmap = generate_color_map()
    open("colormap.json",'w').write(json.dumps({str(" ".join([str(y) for y in list(x)])):list(cmap[x]) for x in cmap}))
