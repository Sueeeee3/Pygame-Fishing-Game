import pygame
import math
import fish_data
from settings import WIDTH, HEIGHT
from splash import Splashing, DIFFICULTY_CONFIG

FONT_PATH = "TradeWinds-Regular.ttf"
TYPEWRITER_SPEED = 35

_font_cache = {}
def tw(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return _font_cache[size]


class DialogueLine:
    def __init__(self, text, wait_after=2000, auto_advance=True):
        self.text = text
        self.wait_after = wait_after
        self.auto_advance = auto_advance


class Cutscene:
    def __init__(self):
        self.lines = []
        self.current_line = 0
        self.char_progress = 0.0
        self.line_timer = 0
        self.done = False
        self.waiting_after = False
        self._prev_char_int = -1
        self.setup()

    def setup(self):
        pass

    def _is_police_line(self):
        if self.lines and self.current_line < len(self.lines):
            return self.lines[self.current_line].text.startswith("@")
        return False

    def _draw_dialogue(self, screen, font, text, revealed_chars, gui_rect):
        name_font   = tw(38)
        line_height = name_font.get_linesize() + 4
        box_x = gui_rect.x + 60
        box_w = gui_rect.width - 120
        box_cy = gui_rect.centery

        policeman = text.startswith("@")
        if policeman:
            text = text[1:]
        base_color = (120, 180, 255) if policeman else (255, 255, 255)

        tokens = []
        in_emphasis, buf = False, ""
        for ch in text:
            if ch == "*":
                if buf:
                    tokens.append((buf, in_emphasis))
                    buf = ""
                in_emphasis = not in_emphasis
            elif ch == " ":
                if buf:
                    tokens.append((buf, in_emphasis))
                    buf = ""
                tokens.append((" ", in_emphasis))
            else:
                buf += ch
        if buf:
            tokens.append((buf, in_emphasis))

        char_count, visible_tokens = 0, []
        for word, emph in tokens:
            if word == " ":
                if char_count < revealed_chars:
                    visible_tokens.append((" ", emph))
                    char_count += 1
                continue
            if char_count >= revealed_chars:
                break
            remaining = revealed_chars - char_count
            visible_tokens.append((word[:remaining], emph))
            char_count += len(word)

        layout_lines = []
        current_line_tokens, current_line_w = [], 0
        for word, emph in visible_tokens:
            color = (255, 220, 0) if emph else base_color
            surf = name_font.render(word, True, color)
            w = surf.get_width()
            if word == " ":
                current_line_tokens.append((word, emph, surf))
                current_line_w += w
            elif current_line_w + w > box_w:
                if current_line_tokens:
                    layout_lines.append(current_line_tokens)
                current_line_tokens = [(word, emph, surf)]
                current_line_w = w
            else:
                current_line_tokens.append((word, emph, surf))
                current_line_w += w
        if current_line_tokens:
            layout_lines.append(current_line_tokens)

        total_h = len(layout_lines) * line_height
        start_y = box_cy - total_h // 2
        for li, line_tokens in enumerate(layout_lines):
            line_w = sum(s.get_width() for _, _, s in line_tokens)
            draw_x = box_x + (box_w - line_w) // 2
            draw_y = start_y + li * line_height
            for _, _, surf in line_tokens:
                screen.blit(surf, (draw_x, draw_y))
                draw_x += surf.get_width()

    def update(self, dt, game):
        if self.done or not self.lines or self.current_line >= len(self.lines):
            return

        line = self.lines[self.current_line]
        total_chars = len(line.text.replace("*", "").replace("@", ""))

        if not self.waiting_after:
            self.char_progress += TYPEWRITER_SPEED * dt
            current = int(min(self.char_progress, total_chars))

            if current > self._prev_char_int and self._prev_char_int >= 0 and current <= total_chars:
                if self._is_police_line():
                    game.assets.play_police_type()
                else:
                    game.assets.play_type()
            self._prev_char_int = current

            if self.char_progress >= total_chars:
                self.char_progress = total_chars
                self.waiting_after = True
                self.line_timer = 0
        else:
            self.line_timer += dt * 1000
            if line.auto_advance and self.line_timer >= line.wait_after:
                self._advance(game)

    def _advance(self, game):
        self.current_line += 1
        self.char_progress = 0.0
        self.waiting_after = False
        self.line_timer = 0
        self._prev_char_int = -1
        if self.current_line >= len(self.lines):
            self._on_done(game)

    def handle_click(self, game):
        if self.done or not self.lines or self.current_line >= len(self.lines):
            return
        line = self.lines[self.current_line]
        total = len(line.text.replace("*", "").replace("@", ""))
        if self.char_progress < total:
            self.char_progress = total
            self.waiting_after = True
            self.line_timer = 0
        else:
            self._advance(game)

    def draw(self, screen, assets, font, dt_ms=0):
        pass

    def _on_done(self, game):
        pass


class IntroCutscene(Cutscene):
    FISHBONE_INFO = {
        "name": "Fish Bone", "difficulty": "EASY", "size": 0.9,
        "price": 0, "speed": 1, "image_key": "fishbone", "tier": "EASY",
    }

    
    TUTORIAL_SPLASH_POS = (WIDTH // 2, HEIGHT // 2)

    def __init__(self):
        self.phase = 0
        self.phase_timer = 0.0
        self.tutorial_splash_rect = None  
        self.tutorial_splash_active = False
        self.catch_started = False
        self.catch_won = False
        self.fish_added_cutscene = False
        self.inventory_opened = False
        self.fishpedia_was_open = False
        self.show_rod = False
        self.rod_flash_timer = 0.0
        self.phase_lines = {}
        self.catch_explain_done = False
        self.respawn_timer = 0.0
        self.waiting_respawn = False
        super().__init__()

    def setup(self):
        self.phase_lines = {
            0: [
                DialogueLine("Sooo...", wait_after=1500),
                DialogueLine("You finally decided to quit your day job and earn money through...", wait_after=2000),
                DialogueLine("...Fishing?", wait_after=1500),
                DialogueLine("...", wait_after=1500),
                DialogueLine("Who am I to judge.", wait_after=1800),
            ],
            2: [DialogueLine(
                "See, you have your rod and your bait — feel free to move it around! "
                "But it can't *reach far enough* to catch the more *uncommon* fish..", wait_after=3500,
            )],
            "2_splash_explain": [DialogueLine(
                "Sometimes a *splash* appears on the water — that means a fish is nearby! "
                "Move close and *click it* before it disappears!", wait_after=3000,
            )],
            3: [DialogueLine(
                "Oh! A fish is near! Move your bait *close to the splash* and then *click it* to catch it!",
                wait_after=500, auto_advance=False,
            )],
            "4_explain": [DialogueLine(
                "Now it's all about precision — scroll to pull your *hook* into the green area "
                "to reel the fish in closer!", wait_after=2500,
            )],
            "lost":   [DialogueLine("...Let's try again!", wait_after=1200)],
            "scared": [
                DialogueLine("It ran off! You scared it away.", wait_after=2000),
                DialogueLine("Try not to get too close too fast next time...", wait_after=1800),
            ],
            5: [
                DialogueLine("Ah.. that's not a fish?", wait_after=2000),
                DialogueLine(
                    "Anyway! Check your *inventory* by pressing *I* on your keyboard to see what it is worth.",
                    wait_after=500, auto_advance=False,
                ),
            ],
            6: [
                DialogueLine("...0?", wait_after=1500),
                DialogueLine("Well, there's nothing left but to try again..", wait_after=2000),
                DialogueLine("..It's not like your job will take you back in this economy.", wait_after=2500),
                DialogueLine('And as they say — *"There are plenty of fish in the sea"*', wait_after=2000),
                DialogueLine(
                    "You can check what fish you have unlocked in the *Fishpedia* by pressing the *F* key.",
                    wait_after=500, auto_advance=False,
                ),
            ],
            7: [
                DialogueLine("And don't forget to visit the *Shop* later by pressing *S* on your keyboard.", wait_after=2000),
                DialogueLine("Good luck!", wait_after=2500),
            ],
        }
        self._load_phase(0)

    def _load_phase(self, phase_key):
        self.lines = self.phase_lines.get(phase_key, [])
        self.current_line = 0
        self.char_progress = 0.0
        self.waiting_after = False
        self.line_timer = 0
        self._prev_char_int = -1

    @property
    def phase_dialogue_done(self):
        return self.current_line >= len(self.lines)

    def inventory_locked(self):
        return self.phase not in ("wait_inventory",) and not self.done

    def fishpedia_locked(self):
        return self.phase not in ("wait_fishpedia",) and not self.done

    def _spawn_tutorial_splash(self, game):
       
        import pygame as _pg
        current_time = _pg.time.get_ticks()

       
        frame_surf, _ = game.assets.splash_frames[0]
        w, h = frame_surf.get_size()
        x = self.TUTORIAL_SPLASH_POS[0] - w // 2
        y = self.TUTORIAL_SPLASH_POS[1] - h // 2

    
        game.splashes.clear(game.assets)

        splash_entry = {
            "rect":       _pg.Rect(x, y, w, h),
            "spawn_time": current_time,
            "duration":   8000,   
            "difficulty": "EASY",
            "fish_info":  self.FISHBONE_INFO,
            "_tutorial":  True,   
        }
        game.splashes.splashes.append(splash_entry)
        game.assets.play_splash()

       
        self.tutorial_splash_rect = _pg.Rect(x, y, w, h)
        self.tutorial_splash_active = True
        self.catch_started = False
        self.catch_won = False
        self.waiting_respawn = False

      
        game.catch_mode.active   = False
        game.catch_mode.won      = False
        game.catch_mode.runoff   = False
        game.catch_mode.progress = 0
        game._catch_was_active   = False
        game._catch_was_won      = False
        game._catch_was_runoff   = False

    def _clear_tutorial_splash(self, game):
       
        game.splashes.splashes = [s for s in game.splashes.splashes if not s.get("_tutorial")]
        game.assets.stop_splash()
        self.tutorial_splash_active = False

    def _tutorial_splash_scared(self, game):
       
        if not self.tutorial_splash_active:
            return False
        config = DIFFICULTY_CONFIG["EASY"]
        dist = math.hypot(
            game.fishing.bait_pos.x - self.tutorial_splash_rect.centerx,
            game.fishing.bait_pos.y - self.tutorial_splash_rect.centery,
        )
        return dist < config["scare_dist"] and game.fishing.speed > config["scare_speed"]

    def update(self, dt, game):
        _dialogue_phases = {0, 2, "2_splash_explain", "scared_dialogue",
                            "4_explain", "lost_dialogue", 5, 6, 7}
        if (self.lines and self.current_line < len(self.lines)
                and self.phase in _dialogue_phases
                and not self.waiting_respawn):
            super().update(dt, game)
        self.phase_timer += dt

        if self.phase == 0:
            if self.phase_dialogue_done:
                self.phase = 1
                self.phase_timer = 0.0
                self.show_rod = True

        elif self.phase == 1:
            game.fishing.update()
            self.rod_flash_timer += dt
            if self.rod_flash_timer >= 1.5:
                self.show_rod = False
                self.phase = 2
                self.phase_timer = 0.0
                self._load_phase(2)

        elif self.phase == 2:
            game.fishing.update()
            if self.phase_dialogue_done:
                self.phase = "2_splash_explain"
                self._load_phase("2_splash_explain")

        elif self.phase == "2_splash_explain":
            game.fishing.update()
            if self.phase_dialogue_done:
                self.phase = 3
                self.phase_timer = 0.0
                self._load_phase(3)
                self._spawn_tutorial_splash(game)

        elif self.phase == 3:
            game.fishing.update()
            if self.waiting_respawn:
                self.respawn_timer -= dt
                if self.respawn_timer <= 0:
                    self._spawn_tutorial_splash(game)
                    self._load_phase(3)
                return
          
            game.splashes.update(game.assets)
           
            still_alive = any(s.get("_tutorial") for s in game.splashes.splashes)
            if self.tutorial_splash_active and not still_alive:
                self.tutorial_splash_active = False
                self.phase = "scared_dialogue"
                self._load_phase("scared")
               
                if not game.splashes.scare_message:
                    game.assets.play_fail()

        elif self.phase == "scared_dialogue":
            game.fishing.update()
            if self.phase_dialogue_done:
                self.phase = 3
                self.waiting_respawn = True
                self.respawn_timer = 0.6

        elif self.phase == "4_explain":
            if self.phase_dialogue_done:
                self.catch_explain_done = True
                game.catch_mode.start(self.FISHBONE_INFO)
                self.phase = "4_playing"

        elif self.phase == "4_playing":
            game.catch_mode.update(dt, game.assets)
            if not self.catch_won:
                if game.catch_mode.won:
                    self.catch_won = True
                    if not self.fish_added_cutscene:
                        game.inventory.add_fish(self.FISHBONE_INFO)
                        game.fishpedia.register_catch(self.FISHBONE_INFO)
                        self.fish_added_cutscene = True
                elif game.catch_mode.runoff:
                    self.catch_started = False
                    self._load_phase("lost")
                    self.phase = "lost_dialogue"
            if self.catch_won and not game.catch_mode.active:
                self.phase = 5
                self._load_phase(5)

        elif self.phase == "lost_dialogue":
            if self.phase_dialogue_done:
                self.phase = 3
                self.waiting_respawn = True
                self.respawn_timer = 0.8
                self._clear_tutorial_splash(game)

        elif self.phase == 5:
            if self.phase_dialogue_done:
                self.phase = "wait_inventory"
                pygame.mouse.set_visible(True)

        elif self.phase == "wait_inventory":
            if game.inventory.open:
                self.inventory_opened = True
            if self.inventory_opened and not game.inventory.open:
                self.phase = 6
                self._load_phase(6)
                pygame.mouse.set_visible(False)

        elif self.phase == 6:
            if self.phase_dialogue_done:
                self.phase = "wait_fishpedia"
                pygame.mouse.set_visible(True)

        elif self.phase == "wait_fishpedia":
            if game.fishpedia.open:
                self.fishpedia_was_open = True
            if self.fishpedia_was_open and not game.fishpedia.open:
                self.phase = 7
                self._load_phase(7)
                pygame.mouse.set_visible(False)

        elif self.phase == 7:
            if self.phase_dialogue_done:
                self.done = True
                pygame.mouse.set_visible(True)

    def handle_click(self, game):
        if self.phase == 3 and self.tutorial_splash_active and not self.waiting_respawn:
            mouse_pos = pygame.mouse.get_pos()
            
            fish_info = game.splashes.get_clicked_splash(mouse_pos, game.assets)
            if fish_info:
                self.catch_started = True
                self.tutorial_splash_active = False
                self.phase = "4_explain"
                self._load_phase("4_explain")
                self.catch_explain_done = False
                return
        super().handle_click(game)

    def _should_show_gui(self):
        return self.phase not in {1, 3, "4_playing"}

    def draw(self, screen, assets, font, dt_ms=0):
        gui_w, gui_h = 1750, 350
        gui_x = (WIDTH - gui_w) // 2
        gui_y = HEIGHT - gui_h - 20
        gui_rect = pygame.Rect(gui_x, gui_y, gui_w, gui_h)
        hint_font = tw(30)

        if not self._should_show_gui():
            return

        screen.blit(pygame.transform.scale(assets.gui, (gui_w, gui_h)), (gui_x, gui_y))

        if self.lines and self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            self._draw_dialogue(screen, font, line.text, int(self.char_progress), gui_rect)
            if self.waiting_after and not line.auto_advance:
                hint = hint_font.render("click to continue", True, (180, 180, 180))
                screen.blit(hint, (gui_rect.right - hint.get_width() - 20, gui_rect.bottom - hint.get_height() - 10))
        elif self.phase == "wait_inventory":
            hint = hint_font.render("Press I to open your Inventory", True, (255, 220, 0))
            screen.blit(hint, hint.get_rect(center=gui_rect.center))
        elif self.phase == "wait_fishpedia":
            hint = hint_font.render("Press F to open your Fishpedia", True, (255, 220, 0))
            screen.blit(hint, hint.get_rect(center=gui_rect.center))


class EndingCutscene(Cutscene):
    SPECIAL_FISH_INFO = {
        "name": "Small fish", "difficulty": "SPECIAL", "size": 0.75,
        "price": 9999, "speed": 1, "image_key": "small", "tier": "SPECIAL",
    }

    def __init__(self, player_money):
        self.phase = "catch_win"
        self.phase_timer = 0.0
        self.player_money = player_money
        self.fade_alpha = 0
        self.fade_speed = 80
        self.footsteps_dots = 0
        self.footsteps_timer = 0.0
        self.footsteps_done = False
        self.choice = None
        self._homeless_sound_played = False
        self.credits_lines = [
            "A bad game about fish.",
            "And questionable life choices of me and the main character.",
            "",
            "-Yours trurly, Sue",
            "Thanks for playing <3",
            "",
            "",
            "Now go get a fishing permit!",
        ]
        super().__init__()

    def setup(self):
        self.phase_lines = {
            "reaction": [
                DialogueLine("Wait...!", wait_after=1200),
                DialogueLine("That's an actual fish!", wait_after=1500),
                DialogueLine("It's small but..!", wait_after=1500),
                DialogueLine("*'Small fish in a big pond'* or something like that", wait_after=2500),
            ],
            "police": [],
        }
        self._load_phase("reaction")

    def _load_phase(self, phase_key):
        self.lines = self.phase_lines.get(phase_key, [])
        self.current_line = 0
        self.char_progress = 0.0
        self.waiting_after = False
        self.line_timer = 0
        self._prev_char_int = -1

    @property
    def phase_dialogue_done(self):
        return self.current_line >= len(self.lines)

    def update(self, dt, game):
        if self.lines and self.current_line < len(self.lines):
            super().update(dt, game)
        self.phase_timer += dt

        if self.phase == "catch_win":
            if not game.catch_mode.active:
                self.phase = "reaction"
                self._load_phase("reaction")

        elif self.phase == "reaction":
            if self.phase_dialogue_done:
                self.player_money = game.money
                self.phase_lines["police"] = [
                    DialogueLine("@Policeman : Excuse me, but do you have a fishing permit for this area?", wait_after=2500),
                    DialogueLine("@...", wait_after=1500),
                    DialogueLine(f"@Policeman: Well then, I'm gonna fine you *{self.player_money} Gold*.", wait_after=500, auto_advance=False),
                ]
                self.phase = "footsteps"
                self.footsteps_dots = 0
                self.footsteps_timer = 0.0
                self.footsteps_done = False

        elif self.phase == "footsteps":
            self.footsteps_timer += dt
            if self.footsteps_timer >= 0.35:
                self.footsteps_timer = 0.0
                self.footsteps_dots += 1
                if self.footsteps_dots >= 12:
                    self.footsteps_done = True
                    self.phase = "police"
                    self._load_phase("police")

        elif self.phase == "police":
            if self.phase_dialogue_done:
                self.phase = "choice"
                self.lines = []
                pygame.mouse.set_visible(True)

        elif self.phase == "choice":
            pass

        elif self.phase == "fade_homeless":
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)
            if self.fade_alpha >= 255:
                self.phase = "homeless_text"
                self.phase_timer = 0.0
                pygame.mouse.set_visible(False)

        elif self.phase == "homeless_text":
            if not self._homeless_sound_played:
                self._homeless_sound_played = True
                game.assets.play_fail()
            if self.phase_timer > 4.0:
                self.phase = "credits"
                self.phase_timer = 0.0

        elif self.phase == "credits":
            if self.phase_timer > 6.0:
                self.done = True
                game.running = False

    def _choice_rects(self):
        bw, bh, gap = 460, 100, 40
        total_w = bw * 2 + gap
        btn_y = HEIGHT // 2 + 20
        again_x    = WIDTH // 2 - total_w // 2
        homeless_x = again_x + bw + gap
        return (pygame.Rect(again_x, btn_y, bw, bh),
                pygame.Rect(homeless_x, btn_y, bw, bh))

    def handle_click(self, game):
        if self.phase == "choice":
            mx, my = pygame.mouse.get_pos()
            again_rect, homeless_rect = self._choice_rects()
            if again_rect.collidepoint(mx, my):
                self.choice = "again"
                game.save_system.reset(game)
                game.seen_events.add("intro")
                game.save_system.save(game)
                game.state = "game"
                self.done = True
                pygame.mouse.set_visible(False)
            elif homeless_rect.collidepoint(mx, my):
                self.choice = "homeless"
                self.phase = "fade_homeless"
                self.fade_alpha = 0
        elif self.phase not in ("fade_homeless", "homeless_text", "credits"):
            super().handle_click(game)

    def draw(self, screen, assets, font, dt_ms=0):
        gui_w, gui_h = 1750, 350
        gui_x = (WIDTH - gui_w) // 2
        gui_y = HEIGHT - gui_h - 20
        gui_rect = pygame.Rect(gui_x, gui_y, gui_w, gui_h)
        hint_font = tw(30)
        btn_font  = tw(28)

        if self.phase in ("reaction", "police", "footsteps"):
            screen.blit(pygame.transform.scale(assets.gui, (gui_w, gui_h)), (gui_x, gui_y))

            if self.phase == "footsteps":
                dot_surf = tw(48).render("." * self.footsteps_dots, True, (200, 200, 200))
                screen.blit(dot_surf, dot_surf.get_rect(center=gui_rect.center))
            elif self.lines and self.current_line < len(self.lines):
                line = self.lines[self.current_line]
                self._draw_dialogue(screen, font, line.text, int(self.char_progress), gui_rect)
                if self.waiting_after and not line.auto_advance:
                    hint = hint_font.render("click to continue", True, (180, 180, 180))
                    screen.blit(hint, (gui_rect.right - hint.get_width() - 20, gui_rect.bottom - hint.get_height() - 10))

        elif self.phase == "choice":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            dot_surf = tw(46).render("...", True, (200, 200, 200))
            screen.blit(dot_surf, dot_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

            again_rect, homeless_rect = self._choice_rects()
            mx, my = pygame.mouse.get_pos()
            for rect, label in [(again_rect, "Try Again"), (homeless_rect, "Go back to your day job")]:
                hov = rect.collidepoint(mx, my)
                bg  = pygame.transform.scale(assets.button_hover_img if hov else assets.button_img, rect.size)
                screen.blit(bg, rect.topleft)
                ls = btn_font.render(label, True, (255, 255, 255))
                screen.blit(ls, ls.get_rect(center=rect.center))

        elif self.phase in ("fade_homeless", "homeless_text", "credits"):
            black = pygame.Surface((WIDTH, HEIGHT))
            black.fill((0, 0, 0))
            black.set_alpha(int(self.fade_alpha) if self.phase == "fade_homeless" else 255)
            screen.blit(black, (0, 0))

            if self.phase == "homeless_text":
                msg = tw(72).render("You became homeless.", True, (255, 255, 255))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            elif self.phase == "credits":
                credit_font = tw(40)
                total_h = len(self.credits_lines) * 56
                start_y = HEIGHT // 2 - total_h // 2
                for i, line in enumerate(self.credits_lines):
                    if line:
                        cs = credit_font.render(line, True, (200, 200, 200))
                        screen.blit(cs, cs.get_rect(center=(WIDTH // 2, start_y + i * 56)))


def should_trigger_ending(game):
    all_fish_caught    = all(name in game.fishpedia.caught_fish for name in fish_data.FISH_DATA)
    all_upgrades_owned = all(u["owned"] for u in game.shop.upgrade_items)
    return all_fish_caught and all_upgrades_owned