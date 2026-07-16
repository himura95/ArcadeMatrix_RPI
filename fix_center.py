import glob

for f in glob.glob("engines/clocks/*.py") + ["engines/clock.py"]:
    with open(f, 'r') as file:
        content = file.read()
    
    modified = False
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "start_x = (self.w - tw) // 2 + offset_x" in line and " - left" not in line:
            lines[i] = line.replace("(self.w - tw) // 2 + offset_x", "(self.w - tw) // 2 - left + offset_x")
            modified = True
        elif "y = (self.h - th) // 2 + offset_y" in line and " - top" not in line:
            lines[i] = line.replace("(self.h - th) // 2 + offset_y", "(self.h - th) // 2 - top + offset_y")
            modified = True
            
    if modified:
        with open(f, 'w') as file:
            file.write('\n'.join(lines))
        print("Fixed", f)
