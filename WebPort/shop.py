import pygame
from settings import S, SP, WHITE
#Nothing changed exept making the hardcoded values scale based on settings scaling function and importing settings values

FONT_PATH = "TradeWinds-Regular.ttf"


_font_cache = {}
def tw(size):
    scaled = S(size)
    if scaled not in _font_cache:
        _font_cache[scaled] = pygame.font.Font(FONT_PATH, scaled)
    return _font_cache[scaled]


class Shop:
    def __init__(self):
        self.rod_tier = 1
        self.max_rod_tier = 1
        self.tier2_upgraded = False
        self.tier3_upgraded = False
        self.active_tab = "rods"
        self.open = False
        self.rod_scroll = 0
        self.rod_cosmetic = {1: "default", 2: "default", 3: "default"}
        self.pending_earn = []

        base_prices = {1: 0, 2: 150, 3: 900}
        rod_descs = {
            (1, "default"): "Rusty, held together by duct tape, prayers and a dream.",
            (1, "black"):   "Same rusty rod, now including existential crisis.",
            (1, "pink"):    "Optimistic color for a terrible rod.   (Including Pink tax)",
            (2, "default"): "Actually holds fish. Revolutionary.",
            (2, "black"):   "Almost business casual.",
            (2, "pink"):    "I'm not so sure about the pink and red combo but you do you.   (Including Pink tax)",
            (3, "default"): "Obviously it has to be gold, it doesn't get better than this.",
            (3, "black"):   "Void-colored. Fish and players alike don't see it coming.",
            (3, "pink"):    "Yass girl, go for it! You are worth it.   (Including Pink tax)",
        }

        def make_rod(name, tier, variant, price_mult=1.0, suffix=""):
            base = base_prices[tier]
            return {
                "name": name + suffix,
                "tier": tier,
                "variant": variant,
                "price": 0 if base == 0 else int(base * price_mult),
                "desc": rod_descs.get((tier, variant), "A trusty fishing rod."),
                "owned": tier == 1,
            }

        self.rod_items = []
        for tier, base_name in [(1, "Simple Rod"), (2, "Better Rod"), (3, "Fishcatcher 2.0")]:
            self.rod_items.append(make_rod(base_name, tier, "default"))
            self.rod_items.append(make_rod(base_name, tier, "black", 1.05, " in Black"))
            self.rod_items.append(make_rod(base_name, tier, "pink",  1.15, " in Pink"))

        self.inventory_items = [
            {"name": "Cardboard Box", "tier": 1, "price": 0,   "desc": "How is this still holding on?!",                                          "owned": True},
            {"name": "Bucket",        "tier": 2, "price": 75,  "desc": "Generational classic, may include a hole in the bottom.",                 "owned": False},
            {"name": "Fridge",        "tier": 3, "price": 350, "desc": "Cools the fish down so they aren't that angry about being sold.",         "owned": False},
        ]

        self.upgrade_items = [
            {"name": "Bread Bait",        "price": 0,   "desc": "Well, someone is eating a worse sandwich now.",                                                    "owned": True,  "req_tier": 1, "flag": None},
            {"name": "Worm Bait",         "price": 120, "desc": "Wiggly, irresistible and too cute for its own, doesn't attract normal Fish.",                      "owned": False, "req_tier": 2, "flag": "tier2"},
            {"name": "Professional Bait", "price": 300, "desc": "If fish had legs they would be coming out of the woodwork. Only attracts the most exclusive Fish.", "owned": False, "req_tier": 3, "flag": "tier3"},
        ]

    def _max_unlocked_tier(self):
        return max((r["tier"] for r in self.rod_items if r["owned"]), default=1)

    def get_allowed_tiers(self):
        if self.rod_tier == 1:
            return ["EASY"]
        if self.rod_tier == 2:
            return ["MEDIUM"] if self.tier2_upgraded else ["EASY", "MEDIUM"]
        return ["HARD"] if self.tier3_upgraded else ["EASY", "MEDIUM", "HARD"]

    def toggle(self):
        self.open = not self.open

    def handle_input(self, event, game):
        if not self.open:
            return
        if event.type == pygame.MOUSEWHEEL and self.active_tab == "rods":
            rows = len(self.rod_items) // 3 + (1 if len(self.rod_items) % 3 else 0)
            self.rod_scroll = max(0, min(max(0, rows - 2), self.rod_scroll - event.y))

    def draw(self, screen, assets, font, ui, game):
        if not self.open:
            return

        SW, SH = screen.get_size()
        panel_w = int(SW * 0.88)
        panel_h = int(SH * 0.88)
        panel_x = (SW - panel_w) // 2
        panel_y = (SH - panel_h) // 2

        screen.blit(pygame.transform.scale(assets.shop_bg, (panel_w, panel_h)), (panel_x, panel_y))
        pygame.draw.rect(screen, (120, 70, 30), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=6)

        tab_w = S(200)
        tab_h = S(85)
        tab_x = panel_x + S(12)
        btn_n   = pygame.transform.scale(assets.button_img,       (tab_w, tab_h))
        btn_hov = pygame.transform.scale(assets.button_hover_img, (tab_w, tab_h))

        for i, (tab_id, label) in enumerate([("rods", "Rods"), ("upgrades", "Baits"), ("inventory", "Storage")]):
            ty = panel_y + S(25) + i * (tab_h + S(10))
            if ui.button(btn_n, btn_hov, tab_x, ty, label, font_size=25):
                self.active_tab = tab_id
                self.rod_scroll = 0
            if tab_id == self.active_tab:
                pygame.draw.rect(screen, (255, 200, 80), (tab_x, ty + tab_h - S(4), tab_w, S(4)))

        content_x = panel_x + tab_w + S(20)
        content_y = panel_y + S(12)
        content_w = panel_w - tab_w - S(32)
        content_h = panel_h - S(24)

        screen.set_clip(pygame.Rect(content_x, content_y, content_w, content_h))
        if self.active_tab == "rods":
            self._draw_rods(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        elif self.active_tab == "upgrades":
            self._draw_upgrades(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        elif self.active_tab == "inventory":
            self._draw_inventory_tab(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        screen.set_clip(None)

    def _draw_card(self, screen, x, y, w, h, color=(70, 38, 15, 160), border=(120, 70, 30)):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(color)
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=6)

    def _inactive_button(self, screen, assets, x, y, w, h, label, font_size=30):
        screen.blit(pygame.transform.scale(assets.button_hover_img, (w, h)), (x, y))
        surf = tw(font_size).render(label, True, WHITE)
        screen.blit(surf, surf.get_rect(center=(x + w // 2, y + h // 2)))

    def draw_wrapped_text(self, screen, text, font, color, x, y, max_width, line_height=None):
        if line_height is None:
            line_height = S(24)
        lines, current = [], ""
        for word in text.split():
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, color), (x, y + i * line_height))
        return len(lines) * line_height

    def _draw_rods(self, screen, assets, ui, game, cx, cy, cw, ch):
        cols     = 3
        cell_w   = cw // 3
        cell_h   = S(360)
        img_size = S(180)
        bw = cell_w - S(40)
        bh = S(62)
        color_key_map = {"default": "n", "black": "b", "pink": "p"}
        scroll_offset = self.rod_scroll * cell_h

        buy_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        buy_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        unlocked_tiers = {r["tier"] for r in self.rod_items if r["owned"]}

        f30 = tw(30)
        f20 = tw(20)

        for i, rod in enumerate(self.rod_items):
            col, row = i % cols, i // cols
            x = cx + col * cell_w + S(8)
            y = cy + row * cell_h - scroll_offset + S(8)
            if y + cell_h < cy or y > cy + ch:
                continue

            card_w = cell_w - S(16)
            card_h = cell_h - S(16)
            self._draw_card(screen, x, y, card_w, card_h)
            screen.blit(f30.render(rod["name"], True, WHITE), (x + S(10), y + S(10)))
            self.draw_wrapped_text(screen, rod["desc"], f20, (210, 195, 175), x + S(10), y + S(44), card_w - S(20))

            ck = color_key_map.get(rod["variant"], "n")
            screen.blit(pygame.transform.scale(assets.get_rod(rod["tier"], ck, "r"), (img_size, img_size)),
                        (x + (card_w - img_size) // 2, y + S(75)))

            btn_y  = y + card_h - bh - S(10)
            text_x = x + (card_w - bw) // 2

            already_active = self.rod_tier == rod["tier"] and self.rod_cosmetic.get(rod["tier"]) == rod["variant"]
            can_afford     = game.money >= rod["price"] if rod["price"] > 0 else True
            tier_available = rod["tier"] == 1 or (rod["tier"] - 1) in unlocked_tiers

            if rod["price"] > 0 and not rod["owned"]:
                screen.blit(f20.render(f"{rod['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - S(26)))

            if rod["owned"]:
                if already_active:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Equipped", 26)
                else:
                    if ui.button(buy_n, buy_hv, text_x, btn_y, "Equip", font_size=20):
                        self.rod_cosmetic[rod["tier"]] = rod["variant"]
                        self.rod_tier = rod["tier"]
            elif tier_available:
                if can_afford:
                    if ui.button(buy_n, buy_hv, text_x, btn_y, "Buy", font_size=20):
                        game.money -= rod["price"]
                        rod["owned"] = True
                        if rod["variant"] == "default":
                            self.max_rod_tier = max(self.max_rod_tier, rod["tier"])
                            self.rod_tier = rod["tier"]
                            self.rod_cosmetic[rod["tier"]] = "default"
                        unlocked_tiers.add(rod["tier"])
                else:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Not enough gold", 24)
            else:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Locked", 26)

    def _draw_upgrades(self, screen, assets, ui, game, cx, cy, cw, ch):
        cols     = 3
        cell_w   = cw // 3
        cell_h   = S(360)
        img_size = S(180)
        bw = cell_w - S(40)
        bh = S(62)
        bait_img_map = {None: assets.bread, "tier2": assets.worm, "tier3": assets.prof}

        btn_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        btn_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        f30 = tw(30)
        f20 = tw(20)
        f26 = tw(26)

        for i, upg in enumerate(self.upgrade_items):
            col, row = i % cols, i // cols
            x = cx + col * cell_w + S(8)
            y = cy + row * cell_h + S(8)
            card_w = cell_w - S(16)
            card_h = cell_h - S(16)

            self._draw_card(screen, x, y, card_w, card_h, color=(55, 30, 8, 160), border=(100, 58, 20))
            screen.blit(f30.render(upg["name"], True, WHITE), (x + S(10), y + S(10)))
            self.draw_wrapped_text(screen, upg["desc"], f20, (210, 195, 175), x + S(10), y + S(44), card_w - S(20))
            screen.blit(pygame.transform.scale(bait_img_map.get(upg["flag"], assets.bread), (img_size, img_size)),
                        (x + (card_w - img_size) // 2, y + S(75)))

            btn_y  = y + card_h - bh - S(10)
            text_x = x + (card_w - bw) // 2

            can_afford = game.money >= upg["price"] if upg["price"] > 0 else True
            req_met    = self._max_unlocked_tier() >= upg["req_tier"]
            active = (
                (upg["flag"] is None    and not self.tier2_upgraded and not self.tier3_upgraded) or
                (upg["flag"] == "tier2" and self.tier2_upgraded and not self.tier3_upgraded) or
                (upg["flag"] == "tier3" and self.tier3_upgraded)
            )

            if upg["price"] > 0 and not upg["owned"]:
                screen.blit(f20.render(f"{upg['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - S(26)))

            if upg["owned"]:
                if active:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Active", 26)
                else:
                    surf = f26.render("Owned", True, (160, 160, 160))
                    screen.blit(surf, surf.get_rect(center=(text_x + bw // 2, btn_y + bh // 2)))
            elif not req_met:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, f"Need Tier {upg['req_tier']} rod", 24)
            elif can_afford:
                if ui.button(btn_n, btn_hv, text_x, btn_y, "Buy", font_size=20):
                    game.money -= upg["price"]
                    upg["owned"] = True
                    self._apply_upgrade(upg)
            else:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Not enough gold", 24)

    def _apply_upgrade(self, upg):
        if upg["flag"] == "tier2":
            self.tier2_upgraded = True
            self.tier3_upgraded = False
        elif upg["flag"] == "tier3":
            self.tier3_upgraded = True

    def _draw_inventory_tab(self, screen, assets, ui, game, cx, cy, cw, ch):
        cols     = 3
        cell_w   = cw // 3
        cell_h   = S(360)
        img_size = S(180)
        bw = cell_w - S(40)
        bh = S(62)
        tier_img_map = {1: assets.c_e, 2: assets.b_e, 3: assets.f_e}

        btn_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        btn_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        f30 = tw(30)
        f20 = tw(20)

        for i, inv in enumerate(self.inventory_items):
            col, row = i % cols, i // cols
            x = cx + col * cell_w + S(8)
            y = cy + row * cell_h + S(8)
            card_w = cell_w - S(16)
            card_h = cell_h - S(16)

            self._draw_card(screen, x, y, card_w, card_h, color=(80, 45, 12, 160), border=(140, 85, 35))
            screen.blit(f30.render(inv["name"], True, WHITE), (x + S(10), y + S(10)))
            self.draw_wrapped_text(screen, inv["desc"], f20, (210, 195, 175), x + S(10), y + S(44), card_w - S(20))
            screen.blit(pygame.transform.scale(tier_img_map.get(inv["tier"], assets.b_e), (img_size, img_size)),
                        (x + (card_w - img_size) // 2, y + S(75)))

            btn_y  = y + card_h - bh - S(10)
            text_x = x + (card_w - bw) // 2

            already_equipped = game.inventory.tier == inv["tier"]
            can_afford = game.money >= inv["price"] if inv["price"] > 0 else True

            if inv["price"] > 0 and not inv["owned"]:
                screen.blit(f20.render(f"{inv['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - S(26)))

            if inv["owned"] or inv["price"] == 0:
                if already_equipped:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Equipped", 26)
                else:
                    if ui.button(btn_n, btn_hv, text_x, btn_y, "Equip", font_size=30):
                        game.inventory.tier = inv["tier"]
            elif can_afford:
                if ui.button(btn_n, btn_hv, text_x, btn_y, "Buy", font_size=20):
                    game.money -= inv["price"]
                    inv["owned"] = True
                    game.inventory.tier = inv["tier"]
            else:

                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Not enough gold", 24)
