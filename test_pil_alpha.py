from PIL import Image
import gzip, struct

path = '/Users/red1l/Documents/work/git/perso/ArcadeMatrix_RPi/fighters_64/kfm/walk.fgt.gz'
with gzip.open(path, 'rb') as f:
    f.read(4) # magic
    w, h, count, trans = struct.unpack('<HHHH', f.read(8))
    f.read(count * 2) # delays
    data = f.read(w * h * 2)
    
print(f"trans 565: 0x{trans:04x}")
img = Image.frombytes('RGB', (w, h), data, 'raw', 'BGR;16')

# get top-left pixel, usually it is transparent
pixel = img.getpixel((0,0))
print("Top-left pixel RGB:", pixel)

r_trans = (trans >> 11) << 3
g_trans = ((trans >> 5) & 0x3F) << 2
b_trans = (trans & 0x1F) << 3
print("Manual shift RGB:", r_trans, g_trans, b_trans)

# What if we just use img.getpixel((0,0)) as transparent color?
# PIL has an easy way to make a color transparent!
# But we need RGBA for later pasting.
def make_transparent_fast(img, trans_color):
    # Method 1: getdata / putdata (still a bit slow in python)
    # Method 2: Create a mask using ImageMath
    import PIL.ImageMath
    r, g, b = img.split()
    # mask = 255 where (R!=tr or G!=tg or B!=tb), else 0
    mask = PIL.ImageMath.eval(
        "convert((r != tr) + (g != tg) + (b != tb), 'L') * 255", 
        r=r, g=g, b=b, tr=trans_color[0], tg=trans_color[1], tb=trans_color[2]
    )
    img.putalpha(mask)
    return img

import time
t0 = time.time()
img_rgba = make_transparent_fast(img, pixel)
print("Time to mask:", time.time() - t0)

