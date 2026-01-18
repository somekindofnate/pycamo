import argparse
import cv2
import hashlib
import numpy as np
import random
import sys

# --- PRESET PALETTES ---
PALETTES = {
    "piedmont": ["#1C1C1C", "#263E31", "#8D9967"], # Forest/City Shadows
    "clay":     ["#6A3B28", "#4A5D44", "#8C7B65"], # Red Earth/River Bank
    "concrete": ["#59595B", "#353932", "#8E918F"], # Urban/Industrial
}

# --- SETUP ARGUMENTS ---
parser = argparse.ArgumentParser()
parser.add_argument("--type", help="The specific style of camouflage to generate.", 
                    required=True, 
                    choices=['organic', 'jagged', 'm90', 'brush'])

parser.add_argument("--preset", help="Use a specific color palette.", 
                    choices=PALETTES.keys(), 
                    default="piedmont")

parser.add_argument("--grid", help="Add an occlusion grid", action="store_true")
parser.add_argument("--rain", help="Add rain streaking", action="store_true")
parser.add_argument("--modulation", help="Add digital noise texture to each color layer", action="store_true")
parser.add_argument("--grid_color", help="Grid Color (Hex)")
parser.add_argument("--colors", help="List of hex colors, separated by commas (Overwrites preset)")
parser.add_argument("--limit", help="How many images to generate", default=10)

def hextorgb(hex_code):
    hex_code = hex_code.strip().lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (4, 2, 0))

def status_update(msg):
    """Helper to overwrite the current line in the terminal"""
    sys.stdout.write(f"\r{msg:<80}") # Pad with spaces to clear previous text
    sys.stdout.flush()

def add_rain_streaks(img, color, density=200, length_min=20, length_max=300):
    status_update("Applying streaking pattern...")
    h, w = img.shape[:2]
    for _ in range(np.random.randint(100, 400)):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        length = np.random.randint(length_min, length_max)
        cv2.line(img, (x, y), (x + length, y + length), color, thickness=np.random.randint(3,30))
    return img

def apply_occlusion_grid(base_img, color_grid, width, height, grid_size):
    status_update("Applying occlusion grid...")
    thickness = 10
    for x in range(0, width + 1, grid_size):
        cv2.line(base_img, (x, 0), (x, height), color_grid, thickness)
    for y in range(0, height + 1, grid_size):
        cv2.line(base_img, (0, y), (width, y), color_grid, thickness)
    return base_img

def apply_outline(img, mask, thickness=20):
    mask_uint8 = (mask.astype(np.uint8) * 255)
    k_size = 2 * thickness + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_size, k_size))
    dilated_mask = cv2.dilate(mask_uint8, kernel, iterations=1)
    outline_mask = cv2.subtract(dilated_mask, mask_uint8)
    img[outline_mask == 255] = (0, 0, 0)
    return img

def apply_digital_modulation(img_layer, density=40, scale=40):
    h, w = img_layer.shape[:2]
    scale = max(1, int(scale))
    small_h, small_w = max(1, h // scale), max(1, w // scale)
    noise = np.random.randint(-density, density, (small_h, small_w), dtype=np.int16)
    noise_up = cv2.resize(noise, (w, h), interpolation=cv2.INTER_NEAREST)
    noise_up_3ch = cv2.merge([noise_up, noise_up, noise_up])
    img_int = img_layer.astype(np.int16)
    img_int = cv2.add(img_int, noise_up_3ch)
    return np.clip(img_int, 0, 255).astype(np.uint8)

# --- MASKS ---

def generate_organic_mask(width, height, scale_factor, threshold, noise_layer):
    small_w = width // scale_factor
    small_h = height // scale_factor
    if small_w < 1: small_w = 1
    if small_h < 1: small_h = 1
        
    small_noise = np.random.randint(50, 255, (small_h, small_w), dtype=np.uint8)
    smooth_noise = cv2.resize(small_noise, (width, height), interpolation=cv2.INTER_CUBIC)
    _, mask = cv2.threshold(smooth_noise, threshold, 255, cv2.THRESH_BINARY)
    return (mask > 0) & (noise_layer > 80)

def generate_jagged_mask(width, height, count, size_min, size_max):
    mask = np.zeros((height, width), dtype=np.uint8)
    offsets = [(0, 0), (width, 0), (-width, 0), (0, height), (0, -height), 
               (width, height), (width, -height), (-width, height), (-width, -height)]
    
    for _ in range(count):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        pts = []
        num_pts = random.randint(3, 4) 
        for _ in range(num_pts):
            angle = random.uniform(0, 2 * np.pi)
            r = random.uniform(size_min, size_max)
            x = int(cx + r * np.cos(angle) * random.uniform(0.5, 1.5))
            y = int(cy + r * np.sin(angle))
            pts.append([x, y])
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        for dx, dy in offsets:
            cv2.fillPoly(mask, [pts + [dx, dy]], (255))
    return mask > 0

def generate_m90_mask(width, height, count, threshold):
    mask = np.zeros((height, width), dtype=np.uint8)
    rect = (-width - 100, -height - 100, (3 * width) + 200, (3 * height) + 200)
    subdiv = cv2.Subdiv2D(rect)
    
    points = []
    for _ in range(count):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        points.append((x, y))
        
    for (x, y) in points:
        for dx in [-width, 0, width]:
            for dy in [-height, 0, height]:
                subdiv.insert((float(x + dx), float(y + dy)))
                
    (facets, centers) = subdiv.getVoronoiFacetList([])
    
    guide_w, guide_h = width // 100, height // 100
    if guide_w < 1: guide_w = 1
    if guide_h < 1: guide_h = 1
    guide_noise = np.random.randint(0, 255, (guide_h, guide_w), dtype=np.uint8)
    guide_map = cv2.resize(guide_noise, (width, height), interpolation=cv2.INTER_CUBIC)
    
    for i, facet in enumerate(facets):
        center = centers[i]
        cx, cy = int(center[0]), int(center[1])
        if 0 <= cx < width and 0 <= cy < height:
            safe_x = min(max(cx, 0), width - 1)
            safe_y = min(max(cy, 0), height - 1)
            val = guide_map[safe_y, safe_x]
            if val > threshold:
                pts = np.array(facet, dtype=np.int32)
                cv2.fillPoly(mask, [pts], (255))
    return mask > 0

def generate_brush_mask(width, height, count, length_min, length_max):
    mask = np.zeros((height, width), dtype=np.uint8)
    offsets = [(0, 0), (width, 0), (-width, 0), (0, height), (0, -height), 
               (width, height), (width, -height), (-width, height), (-width, -height)]
    
    for _ in range(count):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        
        angle_deg = random.randint(25, 65) 
        angle_rad = np.deg2rad(angle_deg)
        length = random.randint(length_min, length_max)
        max_stroke_width = random.randint(int(length * 0.1), int(length * 0.25))
        
        dx = np.cos(angle_rad) * (length / 2)
        dy = np.sin(angle_rad) * (length / 2)
        p0 = np.array([cx - dx, cy - dy])
        p2 = np.array([cx + dx, cy + dy])
        
        bend_direction = 1 if random.random() > 0.5 else -1
        bend_strength = random.randint(int(length * 0.2), int(length * 0.5))
        nx = -np.sin(angle_rad)
        ny = np.cos(angle_rad)
        mid = (p0 + p2) / 2
        p1 = mid + np.array([nx, ny]) * (bend_strength * bend_direction)
        
        steps = 20
        t_vals = np.linspace(0, 1, steps)
        spine = []
        for t in t_vals:
            point = ((1-t)**2 * p0) + (2*(1-t)*t * p1) + (t**2 * p2)
            spine.append(point)
            
        left_side = []
        right_side = []
        for i in range(len(spine) - 1):
            curr_p = spine[i]
            next_p = spine[i+1]
            local_dx = next_p[0] - curr_p[0]
            local_dy = next_p[1] - curr_p[1]
            dist = np.hypot(local_dx, local_dy)
            if dist == 0: continue
            
            local_nx = -local_dy / dist
            local_ny = local_dx / dist
            t_progress = i / (steps - 1)
            taper = 1 - (2 * t_progress - 1)**2 
            base_w = (max_stroke_width * taper) + 5
            
            jitter_l = random.randint(-50, 50) 
            jitter_r = random.randint(-50, 100)
            w_left = max(2, base_w + jitter_l)
            w_right = max(2, base_w + jitter_r)
            
            lx = int(curr_p[0] + local_nx * w_left)
            ly = int(curr_p[1] + local_ny * w_left)
            rx = int(curr_p[0] - local_nx * w_right)
            ry = int(curr_p[1] - local_ny * w_right)
            left_side.append([lx, ly])
            right_side.append([rx, ry])
            
        poly = np.array(left_side + right_side[::-1], dtype=np.int32)
        poly = poly.reshape((-1, 1, 2))
        
        for off_x, off_y in offsets:
            cv2.fillPoly(mask, [poly + [off_x, off_y]], (255))
            
    return mask > 0

def create_camo(width, height, grid_size, args):
    if args.grid_color: color_grid = hextorgb(args.grid_color)
    else: color_grid = (20, 20, 20)

    if args.colors:
        color_list = [c.strip() for c in args.colors.split(',')]
    else:
        color_list = PALETTES[args.preset]

    status_update("Generating base digital noise...")
    noise_scale = np.random.randint(100, 255)
    low_h, low_w = height // noise_scale, width // noise_scale
    noise_raw = np.random.randint(150, 255, (low_h, low_w), dtype=np.uint8)
    noise_layer = cv2.resize(noise_raw, (width, height), interpolation=cv2.INTER_NEAREST)
    
    base_img = cv2.merge([noise_layer, noise_layer, noise_layer])
    base_img = (base_img * 0.2).astype(np.uint8) + 30

    status_update(f"Generating layers ({len(color_list)} cols, {args.type})...")

    total_layers = len(color_list)

    for i, hex_color in enumerate(color_list):
        rgb = hextorgb(hex_color)
        progress = i / total_layers
        
        mask = None
        
        if args.type == 'brush' and i == 0:
            mask = np.ones((height, width), dtype=bool)
            
        elif args.type == 'brush':
            count = max(20, int(80 - (progress * 60)))
            l_min = int(800 - (progress * 100))
            l_max = int(3000 - (progress * 200))
            mask = generate_brush_mask(width, height, count, l_min, l_max)

        elif args.type == 'm90':
            count = 150 
            target_thresh = 50 + (progress * 150)
            thresh = int(target_thresh + random.randint(-20, 20))
            mask = generate_m90_mask(width, height, count, thresh)
            
        elif args.type == 'jagged':
            count = int(np.random.randint(150,800) - (progress * 100)) + random.randint(-20, 20)
            s_min = int(200 - (progress * 50))
            s_max = int(500 - (progress * 200))
            mask = generate_jagged_mask(width, height, count, s_min, s_max)
            
        elif args.type == 'organic':
            target_thresh = 90 + (progress * 100) 
            thresh = int(target_thresh + random.randint(-10, 10))
            thresh = max(50, min(thresh, 250))
            target_scale = 700 - (progress * 200) 
            scale = int(target_scale + random.randint(-50, 50))
            mask = generate_organic_mask(width, height, scale, thresh, noise_layer)

        layer = np.full((height, width, 3), rgb, dtype=np.uint8)

        if args.modulation:
            mod_density = 20
            mod_scale = random.randint(20, 60) 
            layer = apply_digital_modulation(layer, density=mod_density, scale=mod_scale)
        
        base_img[mask] = layer[mask]
        
        if not (args.type == 'brush' and i == 0):
            outline_thickness = max(10, int(35 - (progress * 15)))
            base_img = apply_outline(base_img, mask, thickness=outline_thickness)

    if args.rain:
        base_img = add_rain_streaks(base_img, color_grid)
        
    if args.grid:
        base_img = apply_occlusion_grid(base_img, color_grid, width, height, grid_size)

    return base_img

if __name__ == "__main__":
    WIDTH = 7200  
    HEIGHT = 7200
    GRID_PX = 600 
    
    args = parser.parse_args()
    limit = int(args.limit)

    for i in range(limit):
        camo_img = create_camo(WIDTH, HEIGHT, GRID_PX, args)
        file_hash = hashlib.md5(camo_img.tobytes()).hexdigest()[:8]
        filename = f"output/camo_{file_hash}.png"
        cv2.imwrite(filename, camo_img, [cv2.IMWRITE_PNG_COMPRESSION, 4])
        # Overwrite the last status message with the final result
        sys.stdout.write(f"\rGenerated {filename}" + " " * 40 + "\n")