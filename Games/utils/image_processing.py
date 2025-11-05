import cv2
import numpy as np

# ---------- STYLE / CONSTANTS ----------
MARGIN = 16
TOPBAR_H = 60
BOTTOMBAR_H = 80
SHADOW_OFFSET = 8

# Colors (RGB)
BG = (248, 250, 255)
BG_DARK = (40, 45, 60) # Dark background for lose screen
PANEL = (255, 255, 255)
PANEL_BORDER = (190, 205, 255)
PANEL_SHADOW = (220, 228, 255)

TEXT = (40, 50, 70)
TEXT_SUB = (90, 105, 140)
GOOD = (0, 180, 120)
BAD = (210, 60, 80)
ACCENT = (90, 130, 255)
ACCENT_DARK = (60, 100, 230)
GRAY = (120, 120, 120)

def cv_color(rgb):
    return (rgb[2], rgb[1], rgb[0])

def make_bg(h, w, rgb):
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:, :] = np.array(cv_color(rgb), dtype=np.uint8)[None, None, :]
    return frame

def draw_panel(img, rect, fill, border, border_th=2, shadow=True):
    x, y, w, h = rect
    if shadow:
        sx, sy = x + SHADOW_OFFSET, y + SHADOW_OFFSET
        cv2.rectangle(img, (sx, sy), (sx + w, sy + h), cv_color(PANEL_SHADOW), -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(fill), -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), cv_color(border), border_th)

def put_center_text(img, text, center_xy, font_scale, color, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
    size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = int(center_xy[0] - size[0] / 2)
    y = int(center_xy[1] + size[1] / 2)
    cv2.putText(img, text, (x, y), font, font_scale, cv_color(color), thickness, cv2.LINE_AA)

def draw_image_in_panel(img, picture_bgr, fit_rect):
    x, y, w, h = fit_rect
    draw_panel(img, (x, y, w, h), PANEL, PANEL_BORDER, 2, shadow=True)
    if picture_bgr is None:
        put_center_text(img, "Image missing", (x + w // 2, y + h // 2), 1.0, TEXT)
        return
    ph, pw = picture_bgr.shape[:2]
    s = min(w / max(1, pw), h / max(1, ph))
    nw, nh = int(pw * s), int(ph * s)
    resized = cv2.resize(picture_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    ox = x + (w - nw) // 2
    oy = y + (h - nh) // 2
    img[oy:oy + nh, ox:ox + nw] = resized

def draw_tick_or_cross_over_image(img, fit_rect, correct=True):
    x, y, w, h = fit_rect
    size = int(min(w, h) * 0.42)
    center_x, center_y = x + w // 2, y + h // 2
    thickness = max(8, int(size * 0.1))
    color = GOOD if correct else BAD

    if correct:
        pt1 = (center_x - size // 3, center_y)
        pt2 = (center_x - size // 8, center_y + size // 4)
        pt3 = (center_x + size // 2, center_y - size // 4)
        cv2.line(img, pt1, pt2, cv_color(color), thickness)
        cv2.line(img, pt2, pt3, cv_color(color), thickness)
    else:
        offset = size // 3
        cv2.line(img, (center_x - offset, center_y - offset), (center_x + offset, center_y + offset), cv_color(color), thickness)
        cv2.line(img, (center_x + offset, center_y - offset), (center_x - offset, center_y + offset), cv_color(color), thickness)