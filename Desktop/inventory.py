import pygame
import math

FONT_PATH = "TradeWinds-Regular.ttf"

_font_cache = {}
def tw(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return _font_cache[size]


class Inventory:
    def __init__(self, assets):
        self.assets = assets
        self.tier = 1
        self.items = []
        self.open = False
        self.scroll = 0
        self.pending_sell = []

        self.tier_config = {
            1: {"capacity": 5,  "empty": assets.c_e, "half": assets.c_h, "full": assets.c_f},
            2: {"capacity": 10, "empty": assets.b_e, "half": assets.b_h, "full": assets.b_f},
            3: {"capacity": 30, "empty": assets.f_e, "half": assets.f_h, "full": assets.f_f},
        }

    def get_capacity(self):
        return self.tier_config[self.tier]["capacity"]

    def is_full(self):
        return len(self.items) >= self.get_capacity()

    def add_fish(self, fish_info):
        if not self.is_full():
            self.items.append(fish_info)
            return True
        return False

    def sell_fish(self, index):
        if 0 <= index < len(self.items):
            fish = self.items.pop(index)
            return int(fish["price"] * fish["size"])
        return 0

    def sell_all(self):
        total = sum(int(f["price"] * f["size"]) for f in self.items)
        self.items.clear()
        self.scroll = 0
        return total

    def get_bucket_image(self):
        config = self.tier_config[self.tier]
        count  = len(self.items)
        if count == 0:
            return config["empty"]
        return config["full"] if count >= self.get_capacity() else config["half"]

    def toggle(self):
        self.open = not self.open

    def handle_input(self, event, fishpedia):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            if not fishpedia.open:
                self.toggle()
        if event.type == pygame.MOUSEWHEEL and self.open:
            max_scroll = max(0, math.ceil(len(self.items) / 3) - 2)
            self.scroll = max(0, min(max_scroll, self.scroll - event.y))

    def draw_bucket(self, screen, pos):
        screen.blit(self.get_bucket_image(), pos)

    def draw_inventory(self, screen, font, assets, ui):
        if not self.open:
            return

        SW, SH = screen.get_size()
        panel_w = int(SW * 0.88)
        panel_h = int(SH * 0.88)
        panel_x = (SW - panel_w) // 2
        panel_y = (SH - panel_h) // 2

        inv_bg = pygame.transform.scale(assets.inventory_bg, (panel_w, panel_h))
        screen.blit(inv_bg, (panel_x, panel_y))
        tint = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        tint.fill((180, 210, 240, 40))
        screen.blit(tint, (panel_x, panel_y))
        pygame.draw.rect(screen, (100, 140, 190), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=6)

     
        f24 = tw(24)
        f40 = tw(40)
        f20 = tw(20)
        f25 = tw(25)
        f30 = tw(30)

        count, capacity = len(self.items), self.get_capacity()
        count_surf = f24.render(f"{count} / {capacity}", True, (255, 255, 255))
        badge_w, badge_h = count_surf.get_width() + 28, count_surf.get_height() + 12
        screen.blit(pygame.transform.scale(assets.button_img, (badge_w, badge_h)), (panel_x + 15, panel_y + 15))
        screen.blit(count_surf, (panel_x + 29, panel_y + 21))

        sa_w, sa_h = 160, 50
        sa_x = panel_x + panel_w - sa_w - 15
        sa_y = panel_y + 15
        
        sa_n  = pygame.transform.scale(assets.button_img,       (sa_w, sa_h))
        sa_hv = pygame.transform.scale(assets.button_hover_img, (sa_w, sa_h))
        if ui.button(sa_n, sa_hv, sa_x, sa_y, "Sell All", font_size=25):
            self.pending_sell.append(self.sell_all())

        screen.set_clip(pygame.Rect(panel_x, panel_y, panel_w, panel_h))

        cols    = 3
        cell_w  = panel_w // cols
        top_pad = 80
        cell_h  = (panel_h - top_pad) // 2
        img_size = min(cell_w - 80, cell_h // 2 + 20)
        scroll_offset = self.scroll * cell_h

        sv_w, sv_h = 140, 46
        sell_n  = pygame.transform.scale(assets.button_img,       (sv_w, sv_h))
        sell_hv = pygame.transform.scale(assets.button_hover_img, (sv_w, sv_h))

        size_labels = [
            (1.0,  "Small"),
            (1.10, "Normal"),
            (1.25, "Big"),
            (float("inf"), "Biggest"),
        ]

        sold_indices = []
        for i, fish in enumerate(self.items):
            col, row = i % cols, i // cols
            cx = panel_x + col * cell_w + 10
            cy = panel_y + top_pad + row * cell_h - scroll_offset

            if cy + cell_h < panel_y or cy > panel_y + panel_h:
                continue

            card_w, card_h = cell_w - 20, cell_h - 14
            card_cx = cx + card_w // 2

            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill((220, 235, 255, 160))
            screen.blit(card_surf, (cx, cy))
            pygame.draw.rect(screen, (100, 140, 200), (cx, cy, card_w, card_h), 2, border_radius=6)

            screen.blit(pygame.transform.scale(getattr(assets, fish["image_key"]), (img_size, img_size)),
                        (card_cx - img_size // 2, cy + 8))

            size_label = next(lbl for threshold, lbl in size_labels if fish["size"] < threshold)

            text_y = cy + img_size + 18
            for surf, gap in [
                (f40.render(fish["name"], True, (30, 55, 100)), 6),
                (f20.render(f"Size: {size_label}", True, (60, 100, 160)), 6),
                (f25.render(f"{int(fish['price'] * fish['size'])} Gold", True, (200, 160, 20)), 8),
            ]:
                screen.blit(surf, surf.get_rect(centerx=card_cx, top=text_y))
                text_y += surf.get_height() + gap

            if ui.button(sell_n, sell_hv, card_cx - sv_w // 2, text_y, "Sell", font_size=30):
                sold_indices.append(i)

        for i in sorted(sold_indices, reverse=True):
            self.pending_sell.append(self.sell_fish(i))

        screen.set_clip(None)

        total_rows = math.ceil(len(self.items) / cols) if self.items else 0
        if total_rows > 2:
            sb_x  = panel_x + panel_w - 16
            bar_h = panel_h // total_rows
            bar_y = panel_y + self.scroll * bar_h
            pygame.draw.rect(screen, (150, 185, 220), (sb_x, panel_y, 11, panel_h), border_radius=5)
            pygame.draw.rect(screen, (60,  100, 160), (sb_x, bar_y,   11, bar_h),   border_radius=5)