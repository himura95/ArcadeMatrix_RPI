from PIL import Image, ImageDraw, ImageFont
import random

class TetrisClock:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.blocks = []
        self.last_time_str = ""
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), 
            (255, 255, 0), (255, 165, 0), (0, 255, 255), (255, 0, 255)
        ]
        self.gb_colors = [(15, 56, 15), (48, 98, 48)]
        self.block_size = max(2, self.h // 16)
        self.base_dy = self.h / 15.0
        
    def _build_targets(self, time_str, font, offset_x, offset_y, scale_factor=1.0):
        targets_by_char = []
        try:
            bbox = font.getbbox(time_str)
            left, top = bbox[0], bbox[1]
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except:
            try:
                tw, th = font.getsize(time_str)
                left, top = 0, 0
            except:
                tw, th = 30, 10
                left, top = 0, 0
                
        scaled_tw = tw * scale_factor
        scaled_th = th * scale_factor
        
        start_x = (self.w - scaled_tw) // 2 - (left * scale_factor) + offset_x
        y = (self.h - scaled_th) // 2 - (top * scale_factor) + offset_y
        
        current_x = start_x
        for char in time_str:
            # Create a 1-bit mask at scale 1
            try:
                cw = font.getlength(char)
            except:
                try:
                    cw, _ = font.getsize(char)
                except:
                    cw = 6
                    
            mask_w = max(1, int(cw)) + 2
            mask_h = max(1, th) + 2
            
            mask = Image.new('1', (mask_w, mask_h), color=0)
            draw = ImageDraw.Draw(mask)
            draw.fontmode = '1'
            draw.text((1 - left, 1 - top), char, font=font, fill=1)
            
            # Scale it blockily
            if scale_factor > 1:
                try:
                    resample = Image.Resampling.NEAREST
                except AttributeError:
                    resample = Image.NEAREST
                mask = mask.resize((int(mask_w * scale_factor), int(mask_h * scale_factor)), resample)
            
            char_targets = []
            for py in range(0, mask.size[1], int(self.block_size)):
                for px in range(0, mask.size[0], int(self.block_size)):
                    if mask.getpixel((px, py)):
                        # Map back to global coordinates
                        tx = current_x + px - (1 * scale_factor)
                        ty = y + py - (1 * scale_factor)
                        char_targets.append((tx, ty))
            targets_by_char.append(char_targets)
            
            current_x += int(cw * scale_factor)
            
        return targets_by_char

    def tick(self, img, time_str, font, offset_x, offset_y, is_gameboy=False, scale_factor=1.0):
        draw = ImageDraw.Draw(img)
        draw.fontmode = '1'
        
        if self.last_time_str != time_str:
            palette = self.gb_colors if is_gameboy else self.colors
            if len(self.last_time_str) != len(time_str) or not self.blocks:
                # Major change (or init): Drop old blocks out
                for b in self.blocks:
                    b['state'] = 'out'
                    b['dy'] = random.uniform(self.base_dy * 0.5, self.base_dy)
                    
                # Build new targets for all characters
                targets_by_char = self._build_targets(time_str, font, offset_x, offset_y, scale_factor)
                for char_idx, targets in enumerate(targets_by_char):
                    for tx, ty in targets:
                        self.blocks.append({
                            'char_index': char_idx,
                            'x': tx,
                            'y': ty - self.h - random.randint(0, self.h),
                            'tx': tx,
                            'ty': ty,
                            'dy': random.uniform(self.base_dy, self.base_dy * 2.5),
                            'color': random.choice(palette),
                            'state': 'in'
                        })
            else:
                # Only update changed characters
                changed_indices = [i for i in range(len(time_str)) if time_str[i] != self.last_time_str[i]]
                if changed_indices:
                    # Drop blocks belonging to changed characters
                    for b in self.blocks:
                        if b.get('char_index', -1) in changed_indices and b['state'] in ['in', 'fixed']:
                            b['state'] = 'out'
                            b['dy'] = random.uniform(self.base_dy * 0.5, self.base_dy)
                            
                    # Build new targets and add blocks ONLY for changed characters
                    targets_by_char = self._build_targets(time_str, font, offset_x, offset_y, scale_factor)
                    for char_idx in changed_indices:
                        for tx, ty in targets_by_char[char_idx]:
                            self.blocks.append({
                                'char_index': char_idx,
                                'x': tx,
                                'y': ty - self.h - random.randint(0, self.h),
                                'tx': tx,
                                'ty': ty,
                                'dy': random.uniform(self.base_dy, self.base_dy * 2.5),
                                'color': random.choice(palette),
                                'state': 'in'
                            })
                            
            self.last_time_str = time_str
            
        # Physics and Drawing
        new_blocks = []
        for b in self.blocks:
            if b['state'] == 'in':
                b['y'] += b['dy']
                if b['y'] >= b['ty']:
                    b['y'] = b['ty']
                    b['state'] = 'fixed'
                new_blocks.append(b)
            elif b['state'] == 'out':
                b['y'] += b['dy']
                b['dy'] += 0.5 # Gravity acceleration
                if b['y'] < self.h:
                    new_blocks.append(b)
            elif b['state'] == 'fixed':
                new_blocks.append(b)
                
            # Draw the block (with a slight 1px inner border effect by drawing a smaller rect inside)
            draw.rectangle([int(b['x']), int(b['y']), int(b['x']) + self.block_size - 1, int(b['y']) + self.block_size - 1], fill=b['color'])
            
        self.blocks = new_blocks
        return img
