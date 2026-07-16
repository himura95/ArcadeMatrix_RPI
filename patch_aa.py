import os
import glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "draw.fontmode = '1'" in content or 'draw.fontmode = "1"' in content:
        return
        
    if "ImageDraw.Draw" not in content:
        return
        
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    for line in lines:
        new_lines.append(line)
        if "ImageDraw.Draw" in line and "=" in line:
            var_name = line.split("=")[0].strip()
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}{var_name}.fontmode = '1'")
            modified = True
            
    if modified:
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"Patched {filepath}")

for root, _, files in os.walk('.'):
    if 'venv' in root or '.git' in root: continue
    for f in files:
        if f.endswith('.py'):
            patch_file(os.path.join(root, f))
