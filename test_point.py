from PIL import Image
import time

img = Image.new('L', (240, 120))

t0 = time.time()
img.point(lambda x: 0 if x == 0 else 255, 'L')
print("Lambda point:", time.time() - t0)

lut = [0] + [255] * 255
t0 = time.time()
img.point(lut, 'L')
print("LUT point:", time.time() - t0)

