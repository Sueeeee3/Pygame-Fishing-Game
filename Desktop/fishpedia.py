import pygame
import math
import fish_data

FONT_PATH = "TradeWinds-Regular.ttf"

_font_cache = {}
def tw(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return _font_cache[size]

DESCRIPTIONS = {
    "Taiyaki":        "Very oriental gentleman, rumor has it he's sweet on the inside.",
    "Fish_Sauce":     "Less of a fish, more of a condiment. Still counts.",
    "Fish_Bone":      "Just a skeleton. The fish got away so quickly only this was left behind.",
    "Fish_Scale":     "Very judgemental.",
    "Selfish":        "Yes, im talking about you.",
    "Star_Fish":      "Not technically a fish. Still lives in denial.",
    "Jelly_Fish":     "Many wonder how it didn't melt yet.",
    "Fish_Fillet":    "Convenient.",
    "School_of_Fish": "Even if you catch it, it won't share the fundings.",
    "Fish_Cracker":   "Crunchy. Suspiciously crunchy.",
    "Fish_and_Chips": "Comes in a package deal.",
    "Tuna_Cant":      "It can't. It just can't.",
    "Fish_tank":      "Rumored to be the most welcoming to other fish. (Fish not included)",
    "Fish_Taco":      "A taco that swims.",
    "Fish_stick":     "Perfectly rectangular and very crunchy. Nature is amazing.",
    "Fishnet":        "You caught the net instead of the fish...or is this a fish? Either way: Progress.",
    "Catfish":        "Part cat, part fish. Meows underwater.",
    "Silverfish":     "I wonder how it is so fast with all that weight.",
    "SwedishFish":    "Its not actually Swedish, but lets not break its delusions.",
}

CATEGORY_ORDER  = ["EASY", "MEDIUM", "HARD"]
CATEGORY_LABELS = {"EASY": "Common Fish", "MEDIUM": "Uncommon Fish", "HARD": "Rare Fish"}

BG_COLOR     = (240, 233, 215)
BORDER_COLOR = (160, 130, 90)
CARD_COLORS  = {"EASY": (225, 215, 190, 190), "MEDIUM": (210, 198, 168, 190), "HARD": (195, 178, 145, 190)}
CARD_BORDERS = {"EASY": (160, 130, 80),        "MEDIUM": (140, 110, 60),        "HARD": (120, 90, 40)}

SIZE_LABELS = [
    (1.0,        "Small"),
    (1.10,       "Normal"),
    (1.25,       "Big"),
    (float("inf"), "As big as they come"),
]


class Fishpedia:
    def __init__(self, assets):
        self.assets = assets
        self.open = False
        self.scroll = 0
        self.caught_fish = {}

        self.panel_w = int(1920 * 0.88)
        self.panel_h = int(1080 * 0.88)
        self.panel_x = (1920 - self.panel_w) // 2
        self.panel_y = (1080 - self.panel_h) // 2
        self.cols     = 4
        self.img_size = 150
        self.cell_w   = self.panel_w // self.cols
        self.cell_h   = 320

    def register_catch(self, fish_info):
        name = fish_info["name"].replace(" ", "_")
        size = fish_info["size"]
        if name not in self.caught_fish or self.caught_fish[name] < size:
            self.caught_fish[name] = size

    def toggle(self):
        self.open = not self.open

    def handle_input(self, event, inventory):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            if not inventory.open:
                self.toggle()

        if event.type == pygame.MOUSEWHEEL and self.open:
            total_h = 0
            for cat in CATEGORY_ORDER:
                fish = [n for n, i in fish_data.FISH_DATA.items() if i.get("tier") == cat]
                if fish:
                    total_h += 65 + math.ceil(len(fish) / self.cols) * self.cell_h + 20
            max_scroll = math.ceil(max(0, total_h - self.panel_h) / self.cell_h)
            self.scroll = max(0, min(max_scroll, self.scroll - event.y))

    def draw(self, screen, assets):
        if not self.open:
            return

        pygame.draw.rect(screen, BG_COLOR,     (self.panel_x, self.panel_y, self.panel_w, self.panel_h), border_radius=8)
        pygame.draw.rect(screen, BORDER_COLOR, (self.panel_x, self.panel_y, self.panel_w, self.panel_h), 3, border_radius=8)
        screen.set_clip(pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h))

                             
        f50  = tw(50)
        f30  = tw(30)
        f16  = tw(16)
        f22  = tw(22)
        f20  = tw(20)
        f30h = f30.get_height()  

        scroll_offset = self.scroll * self.cell_h
        current_y = self.panel_y + 20 - scroll_offset

        for category in CATEGORY_ORDER:
            fish_in_cat = [(n, i) for n, i in fish_data.FISH_DATA.items() if i.get("tier") == category]
            if not fish_in_cat:
                continue

            if self.panel_y - self.cell_h < current_y < self.panel_y + self.panel_h:
                hx = self.panel_x + 20
                header = f50.render(CATEGORY_LABELS[category], True, (80, 50, 15))
                screen.blit(header, (hx, current_y))
                pygame.draw.line(screen, BORDER_COLOR,
                                 (hx, current_y + header.get_height() + 3),
                                 (hx + header.get_width(), current_y + header.get_height() + 3), 2)
            current_y += 65

            card_color  = CARD_COLORS[category]
            card_border = CARD_BORDERS[category]

            for i, (name, info) in enumerate(fish_in_cat):
                col, row = i % self.cols, i // self.cols
                x = self.panel_x + col * self.cell_w + 10
                y = current_y + row * self.cell_h

                if y + self.cell_h < self.panel_y or y > self.panel_y + self.panel_h:
                    continue

                card_w, card_h = self.cell_w - 20, self.cell_h - 14
                is_caught = name in self.caught_fish

                card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                card_surf.fill(card_color)
                screen.blit(card_surf, (x, y))
                pygame.draw.rect(screen, card_border, (x, y, card_w, card_h), 2, border_radius=5)

                fish_img = pygame.transform.scale(getattr(assets, info["image_key"]), (self.img_size, self.img_size))
                img_x = x + (card_w - self.img_size) // 2
                if not is_caught:
                    dark = fish_img.copy()
                    dark.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MIN)
                    screen.blit(dark, (img_x, y + 8))
                else:
                    screen.blit(fish_img, (img_x, y + 8))

                text_y   = y + self.img_size + 16
                text_col = (60, 35, 10) if is_caught else (130, 110, 85)
                display_name = name.replace("_", " ") if is_caught else "???"

                screen.blit(f30.render(display_name, True, text_col), (x + 8, text_y))
                text_y += f30h + 5

                if is_caught:
                   
                    line = ""
                    for word in DESCRIPTIONS.get(name, "A mysterious fish.").split():
                        test = line + word + " "
                        if f16.size(test)[0] > card_w - 16:
                            surf = f16.render(line.strip(), True, (80, 60, 35))
                            screen.blit(surf, (x + 8, text_y))
                            text_y += surf.get_height() + 2
                            line = word + " "
                        else:
                            line = test
                    if line.strip():
                        surf = f16.render(line.strip(), True, (80, 60, 35))
                        screen.blit(surf, (x + 8, text_y))

                    biggest    = self.caught_fish[name]
                    size_label = next(lbl for threshold, lbl in SIZE_LABELS if biggest < threshold)
                    size_surf  = f22.render(f"Best: {size_label}", True, (100, 70, 20))
                    screen.blit(size_surf, (x + 8, y + card_h - size_surf.get_height() - 8))
                else:
                    screen.blit(f20.render("???", True, (150, 130, 100)), (x + 8, text_y))

            current_y += math.ceil(len(fish_in_cat) / self.cols) * self.cell_h + 20

        total_height = current_y - (self.panel_y - scroll_offset)
        if total_height > self.panel_h:
            ratio = self.panel_h / total_height
            bar_h = int(self.panel_h * ratio)
            bar_y = self.panel_y + int(self.scroll * self.cell_h * ratio)
            sb_x  = self.panel_x + self.panel_w - 16
            pygame.draw.rect(screen, (180, 155, 110), (sb_x, self.panel_y, 11, self.panel_h), border_radius=5)
            pygame.draw.rect(screen, (100, 70,  30),  (sb_x, bar_y,        11, bar_h),        border_radius=5)

        screen.set_clip(None)