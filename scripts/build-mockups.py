"""Build 3D-tilted iPhone mockup PNGs for the Roamly site.
- Renders iphone-frame.svg via cairosvg
- Composites the screenshot into the screen rect
- Applies a perspective transform simulating a horizontal rotation
- Synthesizes a thin side-bezel column on the leading edge
- Saves transparent PNGs
"""
import os, math, sys
import cairosvg
from PIL import Image, ImageDraw, ImageFilter

ROOT = '/Users/alexmanning/Desktop/roamly-website'
SVG = f'{ROOT}/assets/iphone-frame.svg'
OUT = f'{ROOT}/assets/screens'

# Screen rect in viewBox coords: (4.12, 3.13, 85.95, 186.89) of (94.19, 193.15)
SCREEN = (4.37/100, 1.62/100, 91.25/100, 96.76/100)  # left%, top%, width%, height%

def find_perspective_coeffs(src_corners, dst_corners):
    """Compute 8-coefficient perspective matrix for PIL's Image.transform."""
    matrix = []
    for (x, y), (X, Y) in zip(dst_corners, src_corners):
        matrix.append([X, Y, 1, 0, 0, 0, -x*X, -x*Y])
        matrix.append([0, 0, 0, X, Y, 1, -y*X, -y*Y])
    import numpy as np
    A = np.array(matrix, dtype=float)
    B = np.array([c for pt in dst_corners for c in pt], dtype=float)
    res = np.linalg.solve(A, B)
    return tuple(res)

def composite_screen(frame_img, screen_path):
    fw, fh = frame_img.size
    sx = int(SCREEN[0] * fw)
    sy = int(SCREEN[1] * fh)
    sw = int(SCREEN[2] * fw)
    sh = int(SCREEN[3] * fh)
    screen = Image.open(screen_path).convert('RGBA')
    # cover-fit
    src_ratio = screen.width / screen.height
    dst_ratio = sw / sh
    if src_ratio > dst_ratio:
        new_h = screen.height
        new_w = int(new_h * dst_ratio)
        crop_x = (screen.width - new_w) // 2
        screen = screen.crop((crop_x, 0, crop_x + new_w, new_h))
    else:
        new_w = screen.width
        new_h = int(new_w / dst_ratio)
        screen = screen.crop((0, 0, new_w, new_h))
    screen = screen.resize((sw, sh), Image.LANCZOS)
    # Mask with rounded corners
    mask = Image.new('L', (sw, sh), 0)
    rr = int(min(sw, sh) * 0.115)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=rr, fill=255)
    screen.putalpha(mask)
    out = frame_img.copy()
    out.paste(screen, (sx, sy), screen)
    return out

def add_side_bezel(img, side='left', strength=0.85):
    """Synthesize the metallic side bezel that appears when phone rotates.
    Adds a thin vertical strip with titanium gradient to the leading edge."""
    w, h = img.size
    # bezel width ~3% of phone width
    bw = max(int(w * 0.018), 4)
    bezel = Image.new('RGBA', (bw, h), (0,0,0,0))
    bd = ImageDraw.Draw(bezel)
    # vertical metallic gradient
    for y in range(h):
        # darker at top/bottom, lighter middle
        t = y / h
        m = math.sin(t * math.pi)  # 0..1..0
        base = int(60 + 90 * m)
        bd.line([(0, y), (bw, y)], fill=(base, base-5, base-10, int(255*strength)))
    # Add highlight stripe
    for x in range(bw):
        alpha_mod = 1 - abs((x - bw/2)/(bw/2)) ** 1.5
        for y in range(h):
            r,g,b,a = bezel.getpixel((x,y))
            r = min(255, int(r + 40 * alpha_mod))
            g = min(255, int(g + 40 * alpha_mod))
            b = min(255, int(b + 40 * alpha_mod))
            bezel.putpixel((x,y), (r,g,b,a))
    if side == 'left':
        img.paste(bezel, (0, 0), bezel)
    else:
        img.paste(bezel, (w-bw, 0), bezel)
    return img

def perspective_tilt(img, rotate_y_deg=-14, rotate_x_deg=4):
    """Apply perspective transform simulating Y/X rotation in degrees.
    The phone's leading edge (left if rotate_y < 0) appears taller/wider."""
    w, h = img.size
    pad = max(w, h) // 4
    # Pad with transparent so the transform doesn't clip
    canvas = Image.new('RGBA', (w + 2*pad, h + 2*pad), (0,0,0,0))
    canvas.paste(img, (pad, pad))
    cw, ch = canvas.size

    # Compute destination corners after rotation
    ry = math.radians(rotate_y_deg)
    rx = math.radians(rotate_x_deg)
    # Half dims in pixels
    hw, hh = w/2, h/2
    cx, cy = cw/2, ch/2
    # 4 corners in 3D: TL, TR, BR, BL
    # Apply rotateY then rotateX, then orthographic project (with slight perspective)
    f = 1800  # focal length in pixels (perspective)
    corners_3d = [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)]
    dst = []
    for x, y, z in corners_3d:
        # rotateY
        x2 = x * math.cos(ry) + z * math.sin(ry)
        z2 = -x * math.sin(ry) + z * math.cos(ry)
        y2 = y
        # rotateX
        y3 = y2 * math.cos(rx) - z2 * math.sin(rx)
        z3 = y2 * math.sin(rx) + z2 * math.cos(rx)
        x3 = x2
        # perspective project
        scale = f / (f - z3)
        px = cx + x3 * scale
        py = cy + y3 * scale
        dst.append((px, py))
    src = [(pad, pad), (pad+w, pad), (pad+w, pad+h), (pad, pad+h)]
    coeffs = find_perspective_coeffs(src, dst)
    return canvas.transform((cw, ch), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

def add_drop_shadow(img, offset=(0, 30), blur=40, opacity=0.32):
    w, h = img.size
    pad = blur * 2
    canvas = Image.new('RGBA', (w + 2*pad, h + 2*pad), (0,0,0,0))
    # Build shadow from alpha channel
    alpha = img.split()[-1]
    shadow = Image.new('RGBA', (w + 2*pad, h + 2*pad), (0,0,0,0))
    sh_layer = Image.new('RGBA', img.size, (15, 10, 5, 0))
    sh_layer.putalpha(alpha.point(lambda p: int(p * opacity)))
    shadow.paste(sh_layer, (pad + offset[0], pad + offset[1]), sh_layer)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    canvas = Image.alpha_composite(canvas, shadow)
    fg = Image.new('RGBA', canvas.size, (0,0,0,0))
    fg.paste(img, (pad, pad), img)
    return Image.alpha_composite(canvas, fg)

def trim(img):
    """Crop to visible content with small padding."""
    bbox = img.split()[-1].getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        pad = 10
        return img.crop((max(0, x0-pad), max(0, y0-pad), min(img.width, x1+pad), min(img.height, y1+pad)))
    return img

def build(screen_name, out_name, ry=-14, rx=4, side='left', frame_w=900):
    print(f'Building {out_name} with ry={ry} rx={rx}...')
    cairosvg.svg2png(url=SVG, write_to='/tmp/mockup/_frame.png', output_width=frame_w)
    frame = Image.open('/tmp/mockup/_frame.png').convert('RGBA')
    composed = composite_screen(frame, f'{OUT}/{screen_name}')
    # bezel skipped — too harsh
    tilted = perspective_tilt(composed, rotate_y_deg=ry, rotate_x_deg=rx)
    tilted = trim(tilted)
    final = add_drop_shadow(tilted, offset=(-20, 35), blur=45, opacity=0.30)
    final.save(f'{OUT}/{out_name}', optimize=True)
    print(f'  -> {OUT}/{out_name} ({final.size})')

# Hero: more dramatic tilt
build('places.png',    'places-3d.png',    ry=-18, rx=6, side='left',  frame_w=900)
# Feature blocks: subtler tilts, alternating direction
build('itinerary.png', 'itinerary-3d.png', ry=-10, rx=3, side='left',  frame_w=800)
build('globe.png',     'globe-3d.png',     ry=10,  rx=3, side='right', frame_w=800)
build('browse.png',    'browse-3d.png',    ry=-10, rx=3, side='left',  frame_w=800)
build('myposts.png',   'myposts-3d.png',   ry=10,  rx=3, side='right', frame_w=800)
print('Done.')
