import os
import sys
import random
import math
import pygame


# ---------- STYLE / CONSTANTS ----------
MARGIN = 24
BOARD_PAD = 16
STRIP_GAP = 8
TOPBAR_H = 80
BOTTOMBAR_H = 90

BG = (248, 250, 255)
PANEL = (255, 255, 255)
PANEL_BORDER = (190, 205, 255)
PANEL_SHADOW = (220, 228, 255)

TEXT = (40, 50, 70)
TEXT_SUB = (90, 105, 140)
ACCENT = (90, 130, 255)
ACCENT_DARK = (60, 100, 230)
GOOD = (0, 180, 120)
HILITE = (255, 180, 80)
GHOST = (236, 240, 255)

# Left number badge
BADGE_BG = (255, 247, 215)
BADGE_BORDER = (210, 190, 150)
BADGE_TEXT = (80, 55, 0)
BADGE_W = 52
BADGE_RADIUS = 12

TITLE = "Picture Strip Puzzle"

# ---------- ASSETS / RANDOM PACKS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "puzzle_sprites")


def asset(*parts):
    return os.path.join(ASSET_DIR, *parts)


# Pair each image with its corresponding background music
IMAGE_FILES = [
    "bheem.jpg",
    "picture.jpg",
    "lion.png",
]
MUSIC_FILES = [
    "bg_music_bheem.wav",       # matches bheem.jpg
    "bg_music_picture.wav",     # matches picture.jpg
    "bg_music_animals.wav",     # matches animals.jpg (used for lion.png here)
]


# Pick a random pair


# Global SFX (you can also make them per-pack if you want)
SWAP_SFX = asset("swap.wav")
WIN_SFX  = asset("win.wav")

DIFFICULTIES = {"Easy": 4, "Medium": 6, "Hard": 8}
DEFAULT_DIFF = "Medium"

MIN_STRIP_H = 60
MAX_WIN_W = 1920
MAX_WIN_H = 1200


# ---------- HELPERS ----------
def load_image_or_placeholder(path, w=1200, h=800):
    # Do NOT convert here (convert requires a display)
    if not os.path.exists(path):
        surf = pygame.Surface((w, h))
        surf.fill((210, 240, 255))
        c = (w//2, h//2)
        pygame.draw.circle(surf, (255, 230, 100), c, min(w, h)//4)
        pygame.draw.circle(surf, (0,0,0), (c[0]-60, c[1]-40), 18)
        pygame.draw.circle(surf, (0,0,0), (c+60, c[1]-40), 18)
        pygame.draw.arc(surf, (0,0,0), (c-90, c[1]-40, 180, 160), math.pi*0.15, math.pi*0.85, 7)
        colors = [(255,0,0),(255,128,0),(255,255,0),(0,200,0),(0,150,255),(150,0,255)]
        for i,cx in enumerate(colors):
            pygame.draw.arc(surf, cx, (80+i*6, 60+i*6, w-160-i*12, h-120-i*12), math.pi, math.pi*2, 8)
        return surf
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return pygame.image.load(path)


def try_play_music(path, vol=0.35):
    try:
        if not os.path.exists(path):
            print(f"[music] file not found: {path}")
            return False
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(-1)
        print(f"[music] playing: {path}")
        return True
    except Exception as e:
        print(f"[music] failed: {e}")
        return False


def restart_bg_music(path, vol=0.35):
    if not pygame.mixer.get_init():
        return
    try:
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)
            print(f"[music] restarted: {path}")
    except Exception as e:
        print(f"[music] restart failed: {e}")


def try_load_sound(path):
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except Exception:
        pass
    return None


def rounded_rect(surface, rect, color, radius=14, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def draw_shadow_panel(surface, rect, radius=16, shadow=8):
    shadow_rect = rect.move(shadow, shadow)
    rounded_rect(surface, shadow_rect, PANEL_SHADOW, radius)
    rounded_rect(surface, rect, PANEL, radius)
    pygame.draw.rect(surface, PANEL_BORDER, rect, width=2, border_radius=radius)


def scale_surface(surface, scale):
    w, h = surface.get_size()
    nw, nh = max(1, int(w*scale)), max(1, int(h*scale))
    return pygame.transform.smoothscale(surface, (nw, nh))


# ---------- UI ELEMENTS ----------
class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.hover = False
        self.active = False

    def draw(self, screen, font):
        base = ACCENT if (self.active or self.hover) else (255,255,255)
        txt_col = (255,255,255) if (self.active or self.hover) else ACCENT_DARK
        rounded_rect(screen, self.rect.move(3,3), PANEL_SHADOW, 12)
        rounded_rect(screen, self.rect, base, 12)
        pygame.draw.rect(screen, ACCENT_DARK, self.rect, 2, border_radius=12)
        label = font.render(self.label, True, txt_col)
        screen.blit(label, (self.rect.centerx - label.get_width()//2,
                            self.rect.centery - label.get_height()//2))

    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                return True
        return False


class Strip:
    def __init__(self, image_scaled, src_rect, correct_index):
        self.image_scaled = image_scaled
        self.src_rect = src_rect
        self.correct_index = correct_index
        self.cache_key = None
        self.cache_surf = None

    def render(self, width, height, font, show_numbers=True):
        key = (width, height, show_numbers)
        if self.cache_key == key and self.cache_surf is not None:
            return self.cache_surf

        pic_w = max(1, width - BADGE_W)
        part = self.image_scaled.subsurface(self.src_rect).copy()
        part_scaled = pygame.transform.smoothscale(part, (pic_w, height))
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        badge_rect = pygame.Rect(0, 0, BADGE_W, height)
        if show_numbers:
            rounded_rect(surf, badge_rect, BADGE_BG, BADGE_RADIUS)
            pygame.draw.rect(surf, BADGE_BORDER, badge_rect, 2, border_radius=BADGE_RADIUS)
            txt = font.render(str(self.correct_index + 1), True, BADGE_TEXT)
            surf.blit(txt, (badge_rect.centerx - txt.get_width()//2,
                            badge_rect.centery - txt.get_height()//2))

        surf.blit(part_scaled, (BADGE_W, 0))

        self.cache_key = key
        self.cache_surf = surf
        return surf


# ---------- SLICING ----------
def slice_rows(image_scaled, rows):
    w, h = image_scaled.get_size()
    base = h // rows
    rem = h - base*rows
    rects, y = [], 0
    for i in range(rows):
        hh = base + (1 if i < rem else 0)
        rects.append(pygame.Rect(0, y, w, hh))
        y += hh
    return rects


def build_strips(image_scaled, rows):
    rects = slice_rows(image_scaled, rows)
    return [Strip(image_scaled, r, i) for i, r in enumerate(rects)]


# ---------- LAYOUT / SIZING ----------
def compute_window_size_for(image_size, rows, display_w, display_h):
    img_w, img_h = image_size
    content_w = img_w + BADGE_W
    content_h = img_h + STRIP_GAP*(rows-1)
    win_w = content_w + 2*(MARGIN + BOARD_PAD + BOARD_PAD)
    win_h = TOPBAR_H + MARGIN + (BOARD_PAD + BOARD_PAD + content_h) + BOTTOMBAR_H + MARGIN
    scale = min(1.0,
                (display_w-40) / max(1, win_w),
                (display_h-60) / max(1, win_h))
    scale = min(scale, MAX_WIN_W/max(1, win_w), MAX_WIN_H/max(1, win_h))
    return scale, int(win_w*scale), int(win_h*scale)


def rebuild_everything(full_img, rows, display_w, display_h):
    img = full_img.copy()
    iw, ih = img.get_size()

    scale, win_w, win_h = compute_window_size_for((iw, ih), rows, display_w, display_h)
    if scale != 1.0:
        img = scale_surface(img, scale)
        iw, ih = img.get_size()

    board_rect = pygame.Rect(MARGIN, TOPBAR_H + MARGIN, win_w - 2*MARGIN, win_h - TOPBAR_H - BOTTOMBAR_H - 2*MARGIN)
    inner_board = board_rect.inflate(-2*BOARD_PAD, -2*BOARD_PAD)
    picture_area = inner_board.inflate(-2*BOARD_PAD, -2*BOARD_PAD)

    strips = build_strips(img, rows)

    stack_w = iw + BADGE_W
    stack_h = ih + STRIP_GAP*(rows-1)
    start_x = picture_area.x + (picture_area.width - stack_w)//2
    start_y = picture_area.y + (picture_area.height - stack_h)//2

    dest_rects = []
    y = start_y
    for i in range(rows):
        natural_h = strips[i].src_rect.height
        h_i = max(MIN_STRIP_H, natural_h)
        dest_rects.append(pygame.Rect(start_x, y, stack_w, h_i))
        y += natural_h + STRIP_GAP

    real_total = sum(r.height for r in dest_rects) + STRIP_GAP*(rows-1)
    shift = (picture_area.height - real_total)//2
    for r in dest_rects:
        r.move_ip(0, shift)

    return img, win_w, win_h, board_rect, inner_board, picture_area, strips, dest_rects


# ---------- MAIN ----------
def main():
    pygame.init()
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    except Exception:
        pass

    info = pygame.display.Info()
    display_w, display_h = info.current_w, info.current_h
    
    rand_idx = random.randrange(min(len(IMAGE_FILES), len(MUSIC_FILES)))
    IMAGE_FILE = asset(IMAGE_FILES[rand_idx])
    MUSIC_FILE = asset(MUSIC_FILES[rand_idx])
    # Load random image from selected pair (no convert yet)
    raw_img = load_image_or_placeholder(IMAGE_FILE)

    title_font = pygame.font.SysFont("Comic Sans MS, Arial Rounded MT Bold", 42, bold=True)
    ui_font = pygame.font.SysFont("Nunito, Comic Sans MS, Arial", 24, bold=True)
    strip_font = pygame.font.SysFont("Baloo, Comic Sans MS, Arial", 28, bold=True)
    win_font = pygame.font.SysFont("Comic Sans MS, Arial Rounded MT Bold", 64, bold=True)

    diff_name = DEFAULT_DIFF
    rows = DIFFICULTIES[diff_name]
    show_numbers = True

    (scaled_img, win_w, win_h, board_rect, inner_board, picture_area,
     strips, dest_rects) = rebuild_everything(raw_img, rows, display_w, display_h)

    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption(TITLE)

    # Convert after display creation for speed
    if raw_img.get_bitsize() in (24, 32):
        raw_img = raw_img.convert()
    scaled_img = scaled_img.convert()

    # Audio
    music_on = try_play_music(MUSIC_FILE, 0.35)
    swap_sfx = try_load_sound(SWAP_SFX)
    win_sfx = try_load_sound(WIN_SFX)

    clock = pygame.time.Clock()

    # Buttons
    btn_w, btn_h = 150, 44
    spacing = 16

    def make_buttons():
        y = win_h - BOTTOMBAR_H + (BOTTOMBAR_H-btn_h)//2
        x = MARGIN
        btns = {}
        btns["Shuffle"] = Button((x, y, btn_w, btn_h), "Shuffle"); x += btn_w + spacing
        for name in ["Easy", "Medium", "Hard"]:
            btns[name] = Button((x, y, 120, btn_h), name); x += 120 + 10
        btns["Numbers"] = Button((x, y, 150, btn_h), f"Numbers: {'On' if show_numbers else 'Off'}"); x += 150 + 10
        btns["Mute"] = Button((win_w - MARGIN - 110, y, 110, btn_h), "Mute" if music_on else "Unmute")
        return btns

    btns = make_buttons()

    order = list(range(rows))
    random.shuffle(order)
    selected_pos = None
    won = False
    confetti = []
    swap_anim = 0.0
    swap_pair = None

    # Win menu state
    win_time = None
    show_win_menu = False
    play_again_btn = None
    exit_btn = None
    win_menu_rect = None

    def make_win_menu_buttons():
        nonlocal play_again_btn, exit_btn
        mw, mh = 420, 200
        menu_rect = pygame.Rect(0, 0, mw, mh)
        menu_rect.center = (win_w // 2, win_h // 2)

        bw, bh = 160, 48
        gap = 24
        by = menu_rect.bottom - 32 - bh
        play_again_btn = Button((menu_rect.centerx - gap//2 - bw, by, bw, bh), "Play Again")
        exit_btn = Button((menu_rect.centerx + gap//2, by, bw, bh), "Exit")
        return menu_rect

    def is_solved():
        return all(order[i] == i for i in range(len(order)))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Event handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                continue

            # If the win menu is visible, only handle its buttons and skip other interactions
            if show_win_menu:
                # Update hover state and handle clicks
                if play_again_btn:
                    play_again_btn.handle(ev)
                if exit_btn:
                    exit_btn.handle(ev)

                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if play_again_btn and play_again_btn.rect.collidepoint(ev.pos):
                        # Pick a new random image/music pair
                        new_idx = random.randrange(min(len(IMAGE_FILES), len(MUSIC_FILES)))
                        new_image_file = asset(IMAGE_FILES[new_idx])
                        new_music_file = asset(MUSIC_FILES[new_idx])

                        # Load new image (no convert yet)
                        new_raw = load_image_or_placeholder(new_image_file)
                        # Rebuild everything with same difficulty
                        (scaled_img, win_w, win_h, board_rect, inner_board, picture_area,
                         strips, dest_rects) = rebuild_everything(new_raw, rows, display_w, display_h)
                        screen = pygame.display.set_mode((win_w, win_h))

                        # Convert after display creation
                        if new_raw.get_bitsize() in (24, 32):
                            new_raw = new_raw.convert()
                        scaled_img = scaled_img.convert()

                        # Update globals to the new image/music
                        raw_img = new_raw
                        # Update module-level paths for reference
                        globals()["IMAGE_FILE"] = new_image_file

                        # Reset order and UI
                        order = list(range(rows))
                        random.shuffle(order)
                        selected_pos = None
                        won = False
                        confetti.clear()
                        swap_anim = 0.0
                        swap_pair = None
                        win_time = None
                        show_win_menu = False
                        win_menu_rect = None

                        # Restart music with the new track
                        globals()["MUSIC_FILE"] = new_music_file
                        restart_bg_music(MUSIC_FILE, 0.35)

                        # Also rebuild bottom bar buttons to match new win_w/win_h
                        btns = make_buttons()

                    elif exit_btn and exit_btn.rect.collidepoint(ev.pos):
                        running = False

                # Skip other UI interactions while popup is active
                continue

            # Button-only controls (not when popup visible)
            for name, b in list(btns.items()):
                if b.handle(ev):
                    if name == "Shuffle":
                        random.shuffle(order); selected_pos=None; won=False
                        confetti.clear(); swap_anim=0.0; swap_pair=None
                        # Restart background music on reset
                        restart_bg_music(MUSIC_FILE, 0.35)

                    elif name in DIFFICULTIES:
                        diff_name = name
                        rows = DIFFICULTIES[diff_name]
                        order = list(range(rows)); random.shuffle(order)
                        (scaled_img, win_w, win_h, board_rect, inner_board, picture_area,
                         strips, dest_rects) = rebuild_everything(raw_img, rows, display_w, display_h)
                        screen = pygame.display.set_mode((win_w, win_h))
                        scaled_img = scaled_img.convert()
                        btns = make_buttons()
                        selected_pos=None; won=False
                        # Restart background music when difficulty changes
                        restart_bg_music(MUSIC_FILE, 0.35)

                    elif name == "Numbers":
                        show_numbers = not show_numbers
                        btns["Numbers"].label = f"Numbers: {'On' if show_numbers else 'Off'}"

                    elif name == "Mute":
                        if pygame.mixer.get_init():
                            if pygame.mixer.music.get_busy():
                                pygame.mixer.music.pause(); btns["Mute"].label="Unmute"
                            else:
                                pygame.mixer.music.unpause(); btns["Mute"].label="Mute"

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not won:
                mx, my = ev.pos
                clicked = None
                for i, r in enumerate(dest_rects):
                    rr = r.inflate(8, 8)
                    if rr.collidepoint(mx, my):
                        clicked = i
                        break
                if clicked is not None:
                    if selected_pos is None:
                        selected_pos = clicked
                    else:
                        if clicked != selected_pos:
                            order[selected_pos], order[clicked] = order[clicked], order[selected_pos]
                            swap_pair = (selected_pos, clicked)
                            swap_anim = 0.15
                            if swap_sfx:
                                try: swap_sfx.play()
                                except Exception: pass
                        selected_pos = None
                        if is_solved():
                            won = True
                            win_time = pygame.time.get_ticks()
                            show_win_menu = False
                            win_menu_rect = None
                            # Stop bg music and play win sfx
                            if pygame.mixer.get_init():
                                try: pygame.mixer.music.stop()
                                except Exception: pass
                            if win_sfx:
                                try: win_sfx.play()
                                except Exception: pass
                            # Confetti
                            cols = [(255,0,0),(255,128,0),(255,220,0),(0,200,120),(0,150,255),(150,0,255),(255,105,180)]
                            confetti = [{
                                "x": random.uniform(0, win_w),
                                "y": random.uniform(-200, -20),
                                "vx": random.uniform(-40, 40),
                                "vy": random.uniform(120, 260),
                                "size": random.randint(4, 9),
                                "color": random.choice(cols)
                            } for _ in range(160)]

        # Updates
        if swap_anim > 0:
            swap_anim -= dt
            if swap_anim < 0: swap_anim = 0
        if won:
            for p in confetti:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["y"] > win_h + 20:
                    p["y"] = random.uniform(-200, -20)
                    p["x"] = random.uniform(0, win_w)

        # After winning, show menu after 3 seconds (non-blocking)
        if won and not show_win_menu:
            if win_time is not None:
                if pygame.time.get_ticks() - win_time >= 3000:  # 3000ms
                    show_win_menu = True
                    win_menu_rect = make_win_menu_buttons()

        # -------- DRAW --------
        screen.fill(BG)

        # Top bar
        draw_shadow_panel(screen, pygame.Rect(12, 10, win_w-24, TOPBAR_H-16), radius=16)
        title = title_font.render("Make the Picture!", True, TEXT)
        subtitle = ui_font.render("Click two strips to swap. Toggle Numbers if you prefer picture-only.", True, TEXT_SUB)
        screen.blit(title, (MARGIN+6, 14))
        screen.blit(subtitle, (MARGIN+8, 14 + title.get_height()))

        # Board panels
        draw_shadow_panel(screen, pygame.Rect(MARGIN, TOPBAR_H + MARGIN,
                                             win_w - 2*MARGIN, win_h - TOPBAR_H - BOTTOMBAR_H - 2*MARGIN), radius=18)
        inner_board = pygame.Rect(MARGIN+BOARD_PAD, TOPBAR_H + MARGIN + BOARD_PAD,
                                  win_w - 2*(MARGIN+BOARD_PAD), win_h - TOPBAR_H - BOTTOMBAR_H - 2*(MARGIN+BOARD_PAD))
        rounded_rect(screen, inner_board, (244, 247, 255), 14)

        # Not solved: draw strips and ghost lanes
        if not won:
            for r in dest_rects:
                pygame.draw.rect(screen, GHOST, r, border_radius=10)

            for pos, r in enumerate(dest_rects):
                idx = order[pos]
                surf = strips[idx].render(r.width, r.height, strip_font, show_numbers=show_numbers)

                rounded_rect(screen, r, PANEL, 12)
                pygame.draw.rect(screen, (230, 235, 255), r, 0, border_radius=12)
                pygame.draw.rect(screen, (205, 215, 245), r, 2, border_radius=12)

                if swap_anim > 0 and swap_pair and (pos in swap_pair):
                    sc = 1.0 + 0.06*(swap_anim/0.15)
                    sw = int(surf.get_width()*sc)
                    sh = int(surf.get_height()*sc)
                    pop = pygame.transform.smoothscale(surf, (sw, sh))
                    screen.blit(pop, (r.centerx - sw//2, r.centery - sh//2))
                else:
                    screen.blit(surf, (r.x, r.y))

                if selected_pos == pos:
                    pygame.draw.rect(screen, HILITE, r.inflate(10,10), 6, border_radius=14)

        # Solved: hide strips and show full image fitted to strips area
        if won:
            stack_left = min(r.x for r in dest_rects)
            stack_right = max(r.right for r in dest_rects)
            stack_top = dest_rects[0].y
            stack_bottom = dest_rects[-1].bottom
            stack_w = stack_right - stack_left
            stack_h = stack_bottom - stack_top

            panel = pygame.Rect(stack_left - 12, stack_top - 12, stack_w + 24, stack_h + 24)
            rounded_rect(screen, panel, PANEL, 18)
            pygame.draw.rect(screen, PANEL_BORDER, panel, 2, border_radius=18)

            fi = raw_img.copy()
            fw, fh = fi.get_size()
            s = min(stack_w / fw, stack_h / fh)
            final_img = pygame.transform.smoothscale(fi, (max(1, int(fw*s)), max(1, int(fh*s))))
            final_rect = final_img.get_rect(center=(stack_left + stack_w//2, stack_top + stack_h//2))
            screen.blit(final_img, final_rect.topleft)

            win_text = win_font.render("You did it!", True, GOOD)
            banner = pygame.Rect(0, 0, win_text.get_width() + 40, win_text.get_height() + 20)
            banner.center = (screen.get_width() // 2, TOPBAR_H - 10)
            rounded_rect(screen, banner, (255, 255, 255), 18)
            pygame.draw.rect(screen, (255, 220, 150), banner, 2, border_radius=18)
            screen.blit(win_text, (banner.x + 20, banner.y + 10))

            for p in confetti:
                pygame.draw.rect(screen, p["color"], (p["x"], p["y"], p["size"], p["size"]))

            # If it's time, draw a modal overlay with the win menu
            if show_win_menu and win_menu_rect:
                # Dim background
                dim = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 100))
                screen.blit(dim, (0, 0))

                # Menu panel
                draw_shadow_panel(screen, win_menu_rect, radius=18)
                title_msg = strip_font.render("What would you like to do?", True, TEXT)
                screen.blit(title_msg, (win_menu_rect.centerx - title_msg.get_width()//2,
                                        win_menu_rect.y + 24))

                # Buttons
                play_again_btn.draw(screen, ui_font)
                exit_btn.draw(screen, ui_font)

        # Bottom bar + buttons
        draw_shadow_panel(screen, pygame.Rect(0, win_h - BOTTOMBAR_H, win_w, BOTTOMBAR_H), radius=16)
        for b in btns.values():
            b.active = (b.label in DIFFICULTIES and b.label == diff_name)
            b.draw(screen, ui_font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
