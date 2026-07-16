from PIL import Image, ImageChops
import gzip, struct, time

path = '/Users/red1l/Documents/work/git/perso/ArcadeMatrix_RPi/fighters_64/kfm/walk.fgt.gz'
with gzip.open(path, 'rb') as f:
    f.read(4) # magic
    w, h, count, trans = struct.unpack('<HHHH', f.read(8))
    f.read(count * 2) # delays
    data = f.read(w * h * 2)

t0 = time.time()
img = Image.frombytes('RGB', (w, h), data, 'raw', 'BGR;16')

# Convert RGB565 trans color to RGB tuple
r = (trans >> 11) << 3
g = ((trans >> 5) & 0x3F) << 2
b = (trans & 0x1F) << 3

# Wait, BGR;16 might shift differently. Let's just sample a transparent pixel
# We assume the top-left pixel is transparent for testing.
trans_color = img.getpixel((0,0)) 

trans_img = Image.new('RGB', img.size, trans_color)
diff = ImageChops.difference(img, trans_img)
mask = diff.convert('L').point(lambda x: 0 if x == 0 else 255, 'L')
img.putalpha(mask)

print("Time with ImageChops:", time.time() - t0)
img.save('test_chops.png')
