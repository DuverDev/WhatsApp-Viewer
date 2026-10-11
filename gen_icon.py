"""Generate app icon for WhatsApp Backup Viewer - original design, no copyright issues."""
from PIL import Image, ImageDraw, ImageFont
import math, os

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = radius
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=fill)

def draw_chat_bubble(draw, cx, cy, w, h, tail_side, fill):
    r = h * 0.28
    x0, y0 = cx - w/2, cy - h/2
    x1, y1 = cx + w/2, cy + h/2
    draw_rounded_rect(draw, (x0, y0, x1, y1), r, fill)
    tw = w * 0.12
    th = h * 0.22
    if tail_side == 'left':
        pts = [(x0 + w*0.12, y1 - h*0.15), (x0 - tw*0.3, y1 + th*0.5), (x0 + w*0.22, y1 - h*0.02)]
    else:
        pts = [(x1 - w*0.12, y1 - h*0.15), (x1 + tw*0.3, y1 + th*0.5), (x1 - w*0.22, y1 - h*0.02)]
    draw.polygon(pts, fill=fill)

def draw_clock_arrow(draw, cx, cy, radius, color, width):
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline=color, width=width)
    draw.line([cx, cy - radius*0.55, cx, cy], fill=color, width=width)
    draw.line([cx, cy, cx + radius*0.45, cy], fill=color, width=width)
    arrow_r = radius * 1.15
    start_angle = -50
    end_angle = 40
    pts = []
    for deg in range(start_angle, end_angle + 1, 3):
        rad = math.radians(deg)
        pts.append((cx + arrow_r * math.cos(rad), cy + arrow_r * math.sin(rad)))
    if len(pts) > 1:
        draw.line(pts, fill=color, width=width)
    ex, ey = pts[-1]
    a = math.radians(end_angle)
    al = width * 2.8
    draw.polygon([
        (ex + al * math.cos(a), ey + al * math.sin(a)),
        (ex + al * math.cos(a + 2.3), ey + al * math.sin(a + 2.3)),
        (ex + al * math.cos(a - 2.3), ey + al * math.sin(a - 2.3)),
    ], fill=color)

def generate_icon(size):
    s = size
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = s * 0.06
    corner = s * 0.22
    bg_color = (0, 150, 120)
    bg_highlight = (0, 170, 135)

    draw_rounded_rect(draw, (margin, margin, s - margin, s - margin), corner, bg_color)
    inner_m = s * 0.08
    draw_rounded_rect(draw, (inner_m, inner_m, s * 0.65, s * 0.55), corner * 0.85, bg_highlight)

    bub_w = s * 0.44
    bub_h = s * 0.26
    bub_cx = s * 0.42
    bub_cy = s * 0.36
    draw_chat_bubble(draw, bub_cx, bub_cy, bub_w, bub_h, 'left', (255, 255, 255))

    line_y = bub_cy - bub_h * 0.1
    line_color = bg_color
    lw = max(1, int(s * 0.018))
    draw.line([bub_cx - bub_w*0.3, line_y, bub_cx + bub_w*0.28, line_y], fill=line_color, width=lw)
    draw.line([bub_cx - bub_w*0.3, line_y + s*0.045, bub_cx + bub_w*0.1, line_y + s*0.045], fill=(*line_color[:3], 140), width=lw)

    bub2_w = s * 0.38
    bub2_h = s * 0.22
    bub2_cx = s * 0.58
    bub2_cy = s * 0.60
    draw_chat_bubble(draw, bub2_cx, bub2_cy, bub2_w, bub2_h, 'right', (220, 253, 237))

    line2_y = bub2_cy - bub2_h * 0.08
    draw.line([bub2_cx - bub2_w*0.28, line2_y, bub2_cx + bub2_w*0.25, line2_y], fill=(0, 130, 100), width=lw)

    clock_r = s * 0.13
    clock_cx = s * 0.74
    clock_cy = s * 0.78
    cw = max(2, int(s * 0.025))

    draw.ellipse([clock_cx - clock_r*1.3, clock_cy - clock_r*1.3,
                  clock_cx + clock_r*1.3, clock_cy + clock_r*1.3], fill=(0, 120, 96))
    draw_clock_arrow(draw, clock_cx, clock_cy, clock_r, (255, 255, 255), cw)

    return img

sizes = [16, 24, 32, 48, 64, 128, 256]
images = [generate_icon(s) for s in sizes]

ico_path = os.path.join(os.path.dirname(__file__), "app.ico")
images[-1].save(ico_path, format='ICO', sizes=[(s, s) for s in sizes],
                append_images=images[:-1])

png_path = os.path.join(os.path.dirname(__file__), "app_icon_256.png")
images[-1].save(png_path, format='PNG')

print(f"app.ico generado ({len(sizes)} tamanos: {sizes})")
print(f"app_icon_256.png generado (preview)")
