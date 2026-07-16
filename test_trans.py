from PIL import Image
import struct

trans = 0x07E0 # Green
trans_bytes = struct.pack('<H', trans)
trans_pixel = Image.frombytes('RGB', (1, 1), trans_bytes, 'raw', 'BGR;16').getpixel((0,0))
print(trans_pixel)
