import pygame

FONT_PATH = "TradeWinds-Regular.ttf"

"""
Shop- manages a shop mechanic for three tabs (Rods, Baits, Storage)

Handles:
-Purchase/equip logic and holds item data
-Draws shop overlay
-Game() passes itself in each call so Shop can read money and deduct costs directly.
"""

#Font cache so each size is only loaded once rather than every draw call
_font_cache = {}
def tw(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return _font_cache[size]


class Shop:
    def __init__(self):
        #Set starting values when Shop is first created;
        self.rod_tier = 1 #Currently equipped rod tier
        self.max_rod_tier = 1 #Highest tier the player has unlocked (Used for purchase logic)
        self.tier2_upgraded = False #Whether Worm Bait upgrade is active
        self.tier3_upgraded = False #Whether Professional Bait upgrade is active
        self.active_tab = "rods" #Tab shown when Shop first opened
        self.open = False #Starts not open
        self.rod_scroll = 0 #Vertical scroll offset for the rods grid (in rows)
        self.rod_cosmetic = {1: "default", 2: "default", 3: "default"} #Active colour variant per tier
        self.pending_earn = [] #Queued gold income to be applied by Game()

        base_prices = {1: 0, 2: 150, 3: 900} #Base rod prices
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
            #Builds a rod item dictionary; Cosmetic varaints cost precentage more than base tier price
            base = base_prices[tier]
            return { 
                "name": name + suffix,
                "tier": tier,
                "variant": variant,
                "price": 0 if base == 0 else int(base * price_mult),
                "desc": rod_descs.get((tier, variant)),
                "owned": tier == 1, #Tier 1 is always pre-owned
            }

        self.rod_items = [] #Array that holds each rods data
        
        for tier, base_name in [(1, "Simple Rod"), (2, "Better Rod"), (3, "Fishcatcher 2.0")]:
            #Generate all 9 rod cards in display order
            self.rod_items.append(make_rod(base_name, tier, "default"))
            self.rod_items.append(make_rod(base_name, tier, "black", 1.05, " in Black"))
            self.rod_items.append(make_rod(base_name, tier, "pink",  1.15, " in Pink"))

        self.inventory_items = [ 
            #List of dictionaries holding all inventory items data
            {"name": "Cardboard Box", "tier": 1, "price": 0,   "desc": "How is this still holding on?!",                                          "owned": True},
            {"name": "Bucket",        "tier": 2, "price": 75,  "desc": "Generational classic, may include a hole in the bottom.",                 "owned": False},
            {"name": "Fridge",        "tier": 3, "price": 350, "desc": "Cools the fish down so they aren't that angry about being sold.",         "owned": False},
        ]

        self.upgrade_items = [ 
            #List of dictionaries holding all bait(upgrades) data
            {"name": "Bread Bait",        "price": 0,   "desc": "Well, someone is eating a worse sandwich now.",                                                    "owned": True,  "req_tier": 1, "flag": None},
            {"name": "Worm Bait",         "price": 120, "desc": "Wiggly, irresistible and too cute for its own, doesn't attract normal Fish.",                      "owned": False, "req_tier": 2, "flag": "tier2"},
            {"name": "Professional Bait", "price": 300, "desc": "If fish had legs they would be coming out of the woodwork. Only attracts the most exclusive Fish.", "owned": False, "req_tier": 3, "flag": "tier3"},
        ]

    def _max_unlocked_tier(self):
        #Check the highest rod tier the player owns; Used for upgrades purchase logic
        return max((r["tier"] for r in self.rod_items if r["owned"]), default=1)

    def get_allowed_tiers(self):
         #Returns which fish difficulty tiers can currently spawn based on rod tier and active bait upgrade (Upgrades focus catched on exlusively new tier)  
        if self.rod_tier == 1:
            return ["EASY"]
        if self.rod_tier == 2:
            return ["MEDIUM"] if self.tier2_upgraded else ["EASY", "MEDIUM"]
        return ["HARD"] if self.tier3_upgraded else ["MEDIUM", "HARD"]

    def toggle(self): 
        #Opening/Closing the Shop overlay
        self.open = not self.open

    def handle_input(self, event, game):
        if not self.open: 
            return
        if event.type == pygame.MOUSEWHEEL and self.active_tab == "rods":
            #Clamp scroll so you can't scroll past the last row of rod cards
            rows = len(self.rod_items) // 3 + (1 if len(self.rod_items) % 3 else 0)
            self.rod_scroll = max(0, min(max(0, rows - 2), self.rod_scroll - event.y))

    def draw(self, screen, assets, font, ui, game):
        if not self.open:
            return

        SW, SH = screen.get_size() 
        panel_w = int(SW * 0.88) #Makes the Shop overlay be 88% window size so game is visible beneath
        panel_h = int(SH * 0.88)
        panel_x = (SW - panel_w) // 2  #Centre the panel on the screen
        panel_y = (SH - panel_h) // 2
        
        #Draws shop background scaled to fit the panel then adds a border around it 
        screen.blit(pygame.transform.scale(assets.shop_bg, (panel_w, panel_h)), (panel_x, panel_y)) 
        pygame.draw.rect(screen, (120, 70, 30), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=6)

        tab_w, tab_h = 200, 85
        tab_x = panel_x + 12
        btn_n   = pygame.transform.scale(assets.button_img,       (tab_w, tab_h))
        btn_hov = pygame.transform.scale(assets.button_hover_img, (tab_w, tab_h))

        #Draws three tab buttons on the left of the screen; Underlines the one which is currently active
        for i, (tab_id, label) in enumerate([("rods", "Rods"), ("upgrades", "Baits"), ("inventory", "Storage")]):
            ty = panel_y + 25 + i * (tab_h + 10)
            if ui.button(btn_n, btn_hov, tab_x, ty, label, font_size=35):
                self.active_tab = tab_id
                self.rod_scroll = 0 #Reset scroll when switching tabs
            if tab_id == self.active_tab:
                pygame.draw.rect(screen, (255, 200, 80), (tab_x, ty + tab_h - 4, tab_w, 4))

        #Content area sits to the right of the tabs column
        content_x = panel_x + tab_w + 20
        content_y = panel_y + 12
        content_w = panel_w - tab_w - 32
        content_h = panel_h - 24

        #Clip to content area so scrolling cards don't bleed over the tab buttons or panel border
        screen.set_clip(pygame.Rect(content_x, content_y, content_w, content_h))
        if self.active_tab == "rods":
            self._draw_rods(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        elif self.active_tab == "upgrades":
            self._draw_upgrades(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        elif self.active_tab == "inventory":
            self._draw_inventory_tab(screen, assets, ui, game, content_x, content_y, content_w, content_h)
        screen.set_clip(None)

    def _draw_card(self, screen, x, y, w, h, color=(70, 38, 15, 160), border=(120, 70, 30)):
        #Semi-transparent card background drawn with SRCALPHA so the shop background shows through
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(color )
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=6) #Add a border around cards

    def _inactive_button(self, screen, assets, x, y, w, h, label, font_size=30):
        #Draws a non-clickable button (Using button hover for visual distinction)
        screen.blit(pygame.transform.scale(assets.button_hover_img, (w, h)), (x, y))
        surf = tw(font_size).render(label, True, (255, 255, 255))
        screen.blit(surf, surf.get_rect(center=(x + w // 2, y + h // 2)))

    def draw_wrapped_text(self, screen, text, font, color, x, y, max_width, line_height=24):
        #Wraps text to fit within max width, returns total height consumed 
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
        #Draws each rod items card
        cols, cell_w, cell_h, img_size = 3, cw // 3, 360, 180
        bw, bh = cell_w - 40, 62
        color_key_map = {"default": "n", "black": "b", "pink": "p"}
        scroll_offset = self.rod_scroll * cell_h #Convert row-based scroll to pixel offset
       
        buy_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        buy_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        unlocked_tiers = {r["tier"] for r in self.rod_items if r["owned"]} #Used to gate tier purchases (Cannot buy tier 3 without buying tier 2 first)

        f30 = tw(30)
        f20 = tw(20)

        
        for i, rod in enumerate(self.rod_items):
            #For each rod item draw a card
            col, row = i % cols, i // cols
            x = cx + col * cell_w + 8
            y = cy + row * cell_h - scroll_offset + 8

            #Skip cards that are fully outside the visible content area
            if y + cell_h < cy or y > cy + ch:
                continue

            card_w, card_h = cell_w - 16, cell_h - 16
            self._draw_card(screen, x, y, card_w, card_h)
            
            screen.blit(f30.render(rod["name"], True, (255, 255, 255)), (x + 10, y + 10))
            self.draw_wrapped_text(screen, rod["desc"], f20, (210, 195, 175), x + 10, y + 44, card_w - 20)

            ck = color_key_map.get(rod["variant"], "n") #Convert variant name to asset suffix
            screen.blit(pygame.transform.scale(assets.get_rod(rod["tier"], ck, "r"), (img_size, img_size)), #Get matching assets image based on suffixes and resize it
                        (x + (card_w - img_size) // 2, y + 75)) #Centre rod image horizontally in card

            btn_y  = y + card_h - bh - 10
            text_x = x + (card_w - bw) // 2

            already_active = self.rod_tier == rod["tier"] and self.rod_cosmetic.get(rod["tier"]) == rod["variant"] #Check if the rod is equipped
            can_afford     = game.money >= rod["price"] if rod["price"] > 0 else True #Check if player can afford rod

            #A tier is purchasable only if the player already owns at least one rod from the tier below
            tier_available = rod["tier"] == 1 or (rod["tier"] - 1) in unlocked_tiers

            #Button state priority; Equipped > Equip > Buy > Not enough gold > Locked
            if rod["price"] > 0 and not rod["owned"]:
                screen.blit(f20.render(f"{rod['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - 26))

            if rod["owned"]:
                if already_active:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Equipped", 26)
                else:
                    if ui.button(buy_n, buy_hv, text_x, btn_y, "Equip", font_size=30):
                        self.rod_cosmetic[rod["tier"]] = rod["variant"] #Switch cosmetic without changing tier
                        self.rod_tier = rod["tier"]
                        
            elif tier_available:
                if can_afford:
                    if ui.button(buy_n, buy_hv, text_x, btn_y, "Buy", font_size=30):
                        game.money -= rod["price"]
                        rod["owned"] = True
                        #Buying the default variant promotes max_rod_tier and auto-equips it
                        #Cosmetic variants just get marked owned without changing the active tier
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
        #Draws each upgrade items card
        cols, cell_w, cell_h, img_size = 3, cw // 3, 360, 180
        bw, bh = cell_w - 40, 62
        bait_img_map = {None: assets.bread, "tier2": assets.worm, "tier3": assets.prof} #Maps upgrade flag to its matching image

        btn_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        btn_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        f30 = tw(30)
        f20 = tw(20)
        f26 = tw(26)

        for i, upg in enumerate(self.upgrade_items):
            #For each upgrade item draw a card
            col, row = i % cols, i // cols
            x = cx + col * cell_w + 8
            y = cy + row * cell_h + 8
            card_w, card_h = cell_w - 16, cell_h - 16

            self._draw_card(screen, x, y, card_w, card_h, color=(55, 30, 8, 160), border=(100, 58, 20))
            screen.blit(f30.render(upg["name"], True, (255, 255, 255)), (x + 10, y + 10))
            self.draw_wrapped_text(screen, upg["desc"], f20, (210, 195, 175), x + 10, y + 44, card_w - 20)
            screen.blit(pygame.transform.scale(bait_img_map.get(upg["flag"], assets.bread), (img_size, img_size)), #Get matching upgrade image based on flag and resize it
                        (x + (card_w - img_size) // 2, y + 75)) #Centre bait image horizontally in card

            btn_y  = y + card_h - bh - 10
            text_x = x + (card_w - bw) // 2

            can_afford = game.money >= upg["price"] if upg["price"] > 0 else True #Check if player can afford upgrade
            req_met    = self._max_unlocked_tier() >= upg["req_tier"] #Player must own the required rod tier first

            #Only one bait is active at a time (The one with highest tier)
            active = (
                (upg["flag"] is None    and not self.tier2_upgraded and not self.tier3_upgraded) or
                (upg["flag"] == "tier2" and self.tier2_upgraded and not self.tier3_upgraded) or
                (upg["flag"] == "tier3" and self.tier3_upgraded)
            )
            
             #Button state priority; Active > Owned > Need Tier X rod > Buy > Not enough gold
            if upg["price"] > 0 and not upg["owned"]:
                screen.blit(f20.render(f"{upg['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - 26))

            if upg["owned"]:
                if active:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Active", 26)
                else:
                    #Owned but superseded by a higher tier upgrade; Show greyed out label
                    surf = f26.render("Owned", True, (160, 160, 160))
                    screen.blit(surf, surf.get_rect(center=(text_x + bw // 2, btn_y + bh // 2)))
                    
            elif not req_met:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, f"Need Tier {upg['req_tier']} rod", 24)
                
            elif can_afford:
                if ui.button(btn_n, btn_hv, text_x, btn_y, "Buy", font_size=30):
                    game.money -= upg["price"]
                    upg["owned"] = True
                    self._apply_upgrade(upg)
            else:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Not enough gold", 24)

    
    def _apply_upgrade(self, upg):
        #Apply the effect of purchased upgrade
        if upg["flag"] == "tier2":
            self.tier2_upgraded = True
            self.tier3_upgraded = False
        elif upg["flag"] == "tier3":
            self.tier3_upgraded = True

    def _draw_inventory_tab(self, screen, assets, ui, game, cx, cy, cw, ch):
        #Draws each inventory items card
        cols, cell_w, cell_h, img_size = 3, cw // 3, 360, 180
        bw, bh = cell_w - 40, 62
        tier_img_map = {1: assets.c_e, 2: assets.b_e, 3: assets.f_e} #Maps storage tier to its matching image

        btn_n  = pygame.transform.scale(assets.button_img,       (bw, bh))
        btn_hv = pygame.transform.scale(assets.button_hover_img, (bw, bh))

        f30 = tw(30)
        f20 = tw(20)

        for i, inv in enumerate(self.inventory_items):
            #For each inventory item draw a card
            col, row = i % cols, i // cols
            x = cx + col * cell_w + 8
            y = cy + row * cell_h + 8
            card_w, card_h = cell_w - 16, cell_h - 16

            self._draw_card(screen, x, y, card_w, card_h, color=(80, 45, 12, 160), border=(140, 85, 35))
            screen.blit(f30.render(inv["name"], True, (255, 255, 255)), (x + 10, y + 10))
            self.draw_wrapped_text(screen, inv["desc"], f20, (210, 195, 175), x + 10, y + 44, card_w - 20)
            screen.blit(pygame.transform.scale(tier_img_map.get(inv["tier"], assets.b_e), (img_size, img_size)), #Get matching storage image based on tier and resize it
                        (x + (card_w - img_size) // 2, y + 75)) #Centre container image horizontally in card

            btn_y  = y + card_h - bh - 10
            text_x = x + (card_w - bw) // 2

            already_equipped = game.inventory.tier == inv["tier"] #Check if this storage item is already equipped
            can_afford = game.money >= inv["price"] if inv["price"] > 0 else True #Check if player can afford storage item

            #Button state priority; Equipped > Equip > Buy > Not enough gold
            if inv["price"] > 0 and not inv["owned"]:
                screen.blit(f20.render(f"{inv['price']} Gold", True, (255, 220, 0)), (text_x, btn_y - 26))

            if inv["owned"] or inv["price"] == 0:
                if already_equipped:
                    self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Equipped", 26)
                else:
                    if ui.button(btn_n, btn_hv, text_x, btn_y, "Equip", font_size=30):
                        game.inventory.tier = inv["tier"]
            elif can_afford:
                if ui.button(btn_n, btn_hv, text_x, btn_y, "Buy", font_size=30):
                    game.money -= inv["price"]
                    inv["owned"] = True
                    game.inventory.tier = inv["tier"] #Auto-equip on purchase 
            else:
                self._inactive_button(screen, assets, text_x, btn_y, bw, bh, "Not enough gold", 24)
