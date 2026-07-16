from PIL import Image
import gzip, struct, time

path = '/Users/red1l/Documents/work/git/perso/ArcadeMatrix_RPi/fighters_64/kfm/walk.fgt.gz'
with gzip.open(path, 'rb') as f:
    f.read(4) # magic
    w, h, count, trans = struct.unpack('<HHHH', f.read(8))
    f.read(count * 2) # delays
    
    data = f.read(w * h * 2)
    print("w, h =", w, h)
    
    t0 = time.time()
    img = Image.frombytes('RGB', (w, h), data, 'raw', 'BGR;16')
    img.save('test_bgr16.png')
    print("Time BGR;16:", time.time() - t0)
