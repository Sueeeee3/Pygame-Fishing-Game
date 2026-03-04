import pygame
import random
import os
import ctypes
import math

from settings import *
from rope import Rope
from fishing import FishingSystem
from catch_mode import CatchMode
from splash import Splashing
from ui import UI
from assets import Assets
from menus import Menus, set_mouse_sensitivity
from shop import Shop
from inventory import Inventory
from save_system import SaveSystem
from fishpedia import Fishpedia
from cutscene import IntroCutscene, EndingCutscene, should_trigger_ending

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Worst Fishing Game EVER")

        self.clock = pygame.time.Clock()
        self.font  = pygame.font.Font("TradeWinds-Regular.ttf", 45)

        self.assets    = Assets()
        self.inventory = Inventory(self.assets)
        self.ui        = UI(self.screen, self.font, self)
        self.menus     = Menus(self)
        self.shop      = Shop()

        self.money                = 0
        self.inventory_full_timer = -2000
        self.fish_added           = False
        self.music_volume         = 1.0
        self.mouse_sensitivity    = 1.0
        self.konami_progress      = 0
        self.cheat_timer          = -5000
        self.show_fps             = False

        self._last_music         = None
        self._inventory_was_open = False
        self._shop_was_open      = False
        self._fishpedia_was_open = False
        self._catch_was_active   = False
        self._catch_was_won      = False
        self._catch_was_runoff   = False
        self._minimised          = False

        self.fishing    = FishingSystem(self.shop, self)
        self.rope       = Rope(self.fishing.rod_pos)
        self.catch_mode = CatchMode()
        self.splashes   = Splashing(self.fishing, self.shop)

        self.state   = "menu"
        self.running = True

        self.FISH_SPLASH_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.FISH_SPLASH_EVENT, random.randint(0, 3000))

        self.save_system = SaveSystem()
        self.fishpedia   = Fishpedia(self.assets)
        self.seen_events = set()
        self.save_system.load_settings_only(self)

        self.special_splash_active   = False
        self.special_splash_rect     = None
        self.ending_cutscene_pending = False
        self.pending_ending_cutscene = False
        self.cutscene                = None

        SPI_GETMOUSESPEED = 0x0070
        original = ctypes.c_int(0)
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(original), 0)
        self.original_mouse_speed = original.value

    def _update_music(self, dt):
        self.assets.set_music_volume(self.music_volume)

        ending = (self.cutscene and not self.cutscene.done
                  and hasattr(self.cutscene, "phase")
                  and self.cutscene.phase in ("choice", "fade_homeless"))
        credits_music = (self.cutscene and not self.cutscene.done
                         and hasattr(self.cutscene, "phase")
                         and self.cutscene.phase in ("homeless_text", "credits"))

        if ending:
            desired = None
        elif credits_music or self.state in ("menu", "options", "options2", "credits") or self.menus.in_game_menu_open:
            desired = self.assets.snd_options
        else:
            desired = self.assets.snd_ambient

        if desired is None:
            if self._last_music is not None:
                self.assets.stop_music()
                self._last_music = None
        elif desired is not self._last_music:
            self._last_music = desired
            self.assets.play_music(desired)

        self.assets.update_music(dt)

    def _update_ui_sounds(self):
        if self.inventory.open and not self._inventory_was_open:
            self.assets.play_ui(self.assets.snd_inventory)
        self._inventory_was_open = self.inventory.open

        if self.shop.open and not self._shop_was_open:
            self.assets.play_ui(self.assets.snd_shop)
        self._shop_was_open = self.shop.open

        if self.fishpedia.open and not self._fishpedia_was_open:
            self.assets.play_ui(self.assets.snd_fishpedia)
        self._fishpedia_was_open = self.fishpedia.open

    def _update_catch_sounds(self):
        if self.state != "game" or self.menus.in_game_menu_open:
            return

        if self.catch_mode.active and not self._catch_was_active:
            self.assets.stop_splash()

        if self.catch_mode.won and not self._catch_was_won:
            self.assets.stop_reel()
            self.assets.play_success()

        if self.catch_mode.runoff and not self._catch_was_runoff:
            self.assets.stop_reel()

        if self.catch_mode.active and not self.catch_mode.won and not self.catch_mode.runoff:
            self.assets.play_reel()
        elif not self.catch_mode.active and self._catch_was_active:
            self.assets.stop_reel()

        self._catch_was_won    = self.catch_mode.won
        self._catch_was_runoff = self.catch_mode.runoff
        self._catch_was_active = self.catch_mode.active

    def new_game(self):
        self.save_system.reset(self)
        self.seen_events             = set()
        self._last_music             = None
        self._catch_was_active       = False
        self._catch_was_won          = False
        self._catch_was_runoff       = False
        self.splashes.clear(self.assets)
        self.state                   = "game"
        self.save_system.save(self)

    def trigger_event_once(self, event_id, cutscene_func):
        if event_id not in self.seen_events:
            cutscene_func()
            self.seen_events.add(event_id)
            self.save_system.save(self)

    def cutscene_intro(self):
        self.cutscene = IntroCutscene()

    def _cutscene_wants_mouse(self):
        if not self.cutscene or self.cutscene.done:
            return False
        c = self.cutscene
        if isinstance(c, IntroCutscene):
            return c.phase in ("wait_inventory", "wait_fishpedia")
        if isinstance(c, EndingCutscene):
            return c.phase == "choice"
        return False

    def _inventory_locked(self):
        if self.cutscene and not self.cutscene.done and isinstance(self.cutscene, IntroCutscene):
            return self.cutscene.phase != "wait_inventory"
        return False

    def _fishpedia_locked(self):
        if self.cutscene and not self.cutscene.done and isinstance(self.cutscene, IntroCutscene):
            return self.cutscene.phase != "wait_fishpedia"
        return False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.ui.update_mouse_state()
            self.handle_events(dt)
            self.update(dt)
            self.draw(dt)
            pygame.display.flip()

        pygame.quit()
        ctypes.windll.user32.SystemParametersInfoW(0x0071, 0, self.original_mouse_speed, 0)

    def handle_events(self, dt):
        for event in pygame.event.get():
            current_time = pygame.time.get_ticks()

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.ACTIVEEVENT:
                if hasattr(event, "state") and event.state & 2:
                    if event.gain == 0:
                        self._minimised = True
                        self.assets.pause_all()
                    else:
                        self._minimised = False
                        self.assets.resume_all()

            if event.type == self.FISH_SPLASH_EVENT and self.state == "game":
                in_cutscene = self.cutscene and not self.cutscene.done
                in_pause    = self.menus.in_game_menu_open
                if not in_cutscene and not in_pause:
                    self.splashes.spawn(current_time, self.assets)
                pygame.time.set_timer(self.FISH_SPLASH_EVENT, random.randint(3000, 7000))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.cutscene and not self.cutscene.done:
                    self.cutscene.handle_click(self)
                else:
                    self.handle_click(event.pos, current_time)

            self.handle_menu_input(event)
            self.handle_game_input(event, current_time, dt)

            if self.state == "game":
                self.shop.handle_input(event, self)

            if not self._inventory_locked():
                self.inventory.handle_input(event, self.fishpedia)
            if not self._fishpedia_locked():
                self.fishpedia.handle_input(event, self.inventory)

    def handle_menu_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE and self.state == "game":
            if self.shop.open:
                self.shop.open = False
                return
            self.save_system.save(self)
            self.menus.in_game_menu_open = not self.menus.in_game_menu_open
            if self.menus.in_game_menu_open:
                self.assets.stop_reel()
                self.assets.stop_splash()
                self.splashes.clear(self.assets)
                self._catch_was_active = False
                self._catch_was_won    = False
                self._catch_was_runoff = False

        if event.key == pygame.K_s and self.state == "game" and not self.catch_mode.active:
            self.shop.toggle()
            if self.shop.open:
                self.inventory.open = False

        if event.key == pygame.K_a and self.state == "game":
            self.show_fps = not self.show_fps

    def handle_game_input(self, event, current_time, dt):
        if self.state != "game" or event.type != pygame.MOUSEWHEEL:
            return
        if self.shop.open:
            return
        if self.inventory.open:
            max_scroll = max(0, math.ceil(len(self.inventory.items) / 3) - 2)
            self.inventory.scroll = max(0, min(max_scroll, self.inventory.scroll - event.y))
        elif self.catch_mode.active:
            self.catch_mode.handle_scroll(event.y)

    def handle_click(self, mouse_pos, current_time):
        if self.state != "game" or self.shop.open:
            return

        if self.special_splash_active:
            if self.special_splash_rect and self.special_splash_rect.collidepoint(mouse_pos):
                self.special_splash_active = False
                self.assets.stop_splash()
                self.catch_mode.start(EndingCutscene.SPECIAL_FISH_INFO)
                self.pending_ending_cutscene = True
            return

        if not self.catch_mode.active and not self.inventory.open:
            if self.inventory.is_full():
                self.inventory_full_timer = pygame.time.get_ticks()
                return
            fish_info = self.splashes.get_clicked_splash(mouse_pos, self.assets)
            if fish_info:
                self.assets.stop_splash()
                name_key = fish_info["name"].replace(" ", "_")
                self.catch_mode.start(fish_info, already_known=name_key in self.fishpedia.caught_fish)

    def _apply_mouse_visibility(self):
        if self.state != "game":
            return
        if self.menus.in_game_menu_open:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            return
        if self.cutscene and not self.cutscene.done:
            pygame.mouse.set_visible(self._cutscene_wants_mouse())
            pygame.event.set_grab(False)
            return
        if self.shop.open or self.inventory.open or self.fishpedia.open:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

    def update(self, dt):
        self._update_music(dt)
        self._update_ui_sounds()
        self._update_catch_sounds()

        if self.state == "game" and not self.menus.in_game_menu_open:
            self.trigger_event_once("intro", self.cutscene_intro)

            if self.ending_cutscene_pending and not self.catch_mode.active:
                self.ending_cutscene_pending = False
                self.special_splash_active   = True
                self.special_splash_rect     = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 - 60, 120, 120)

            if self.pending_ending_cutscene and not self.catch_mode.active:
                self.pending_ending_cutscene = False
                self.cutscene = EndingCutscene(self.money)

            if self.cutscene and not self.cutscene.done:
                pygame.event.set_grab(False)
                self.cutscene.update(dt, self)
                self._flush_rope_and_sales()
                self._apply_mouse_visibility()
                return

            if self.shop.open:
                self._apply_mouse_visibility()
                return

            self._apply_mouse_visibility()

            if not self.catch_mode.active:
                self.splashes.update(self.assets)
                self.fishing.update()
                self.fish_added = False
            else:
                self.catch_mode.update(dt, self.assets)
                if self.catch_mode.won and self.catch_mode.current_fish and not self.fish_added:
                    fish = self.catch_mode.current_fish
                    if fish.get("difficulty") == "SPECIAL":
                        if not self.pending_ending_cutscene:
                            self.pending_ending_cutscene = True
                    else:
                        self.inventory.add_fish(fish)
                        self.fishpedia.register_catch(fish)
                        if (should_trigger_ending(self)
                                and not isinstance(self.cutscene, EndingCutscene)
                                and not self.ending_cutscene_pending
                                and not self.pending_ending_cutscene):
                            self.ending_cutscene_pending = True
                    self.fish_added = True

        self._flush_rope_and_sales()

    def _flush_rope_and_sales(self):
        rod_top    = self.fishing.rod_top
        bait_top   = pygame.Vector2(self.fishing.bait_pos.x, self.fishing.bait_pos.y)
        bait_speed = self.fishing.bait_vel.length()
        self.rope.update(rod_top, bait_top, bait_speed)

        while self.inventory.pending_sell:
            self.money += self.inventory.pending_sell.pop()

    def _draw_gold(self):
        gold_label  = self.font.render("Gold: ", True, (255, 255, 255))
        gold_amount = self.font.render(str(self.money), True, (255, 220, 0))
        pad_x, pad_y = 18, 8
        btn_w = gold_label.get_width() + gold_amount.get_width() + pad_x * 2
        btn_h = gold_label.get_height() + pad_y * 2
        btn_x = self.screen.get_width() - btn_w - 20
        btn_y = 20
        self.screen.blit(pygame.transform.scale(self.assets.button_img, (btn_w, btn_h)), (btn_x, btn_y))
        self.screen.blit(gold_label,  (btn_x + pad_x, btn_y + pad_y))
        self.screen.blit(gold_amount, (btn_x + pad_x + gold_label.get_width(), btn_y + pad_y))

    def _draw_game_scene(self, dt_ms):
        lake_surf = self.assets.get_gif_frame("lake", self.assets.lake_frames, dt_ms)
        self.screen.blit(pygame.transform.scale(lake_surf, (WIDTH, HEIGHT)), (0, 0))

        mx = pygame.mouse.get_pos()[0]
        parallax_x = (mx - WIDTH // 2) * 0.001
        dock_rect = self.assets.dock.get_rect(midbottom=(WIDTH // 2 + parallax_x, HEIGHT))
        self.screen.blit(self.assets.dock, dock_rect)

        cutscene_active = self.cutscene and not self.cutscene.done

        if cutscene_active:
            if isinstance(self.cutscene, EndingCutscene):
                if self.catch_mode.active:
                    self.catch_mode.draw(self.screen, self.assets)
                else:
                    self.fishing.draw(self.screen)
                    self.rope.draw(self.screen, self.fishing.get_depth())
                self.cutscene.draw(self.screen, self.assets, self.font, dt_ms)
            else:
                if self.cutscene.phase == "4_playing":
                    self.catch_mode.draw(self.screen, self.assets)
                else:
                    if self.cutscene.phase == 3:
                        self.splashes.draw(self.screen, self.assets, self.font, dt_ms)
                    self.fishing.draw(self.screen)
                    self.rope.draw(self.screen, self.fishing.get_depth())
                    self.cutscene.draw(self.screen, self.assets, self.font, dt_ms)

                self.inventory.draw_inventory(self.screen, self.font, self.assets, self.ui)
                self.fishpedia.draw(self.screen, self.assets)
                self._draw_gold()
        else:
            if self.catch_mode.active:
                self.fishing.draw(self.screen)
                self.rope.draw(self.screen, self.fishing.get_depth())
                self.catch_mode.draw(self.screen, self.assets)
            else:
                self.splashes.draw(self.screen, self.assets, self.font, dt_ms)
                if self.special_splash_active and self.special_splash_rect:
                    splash_surf = self.assets.get_gif_frame("tutorial_splash", self.assets.splash_frames, dt_ms)
                    self.screen.blit(pygame.transform.scale(splash_surf, (120, 120)), self.special_splash_rect)
                self.fishing.draw(self.screen)
                self.rope.draw(self.screen, self.fishing.get_depth())

            self.inventory.draw_bucket(self.screen, (1530, 870))
            self._draw_gold()

            current_time = pygame.time.get_ticks()
            if current_time - self.inventory_full_timer < 2000 and (current_time // 300) % 2 == 0:
                full_surf = self.font.render("Inventory is full!!", True, (255, 50, 50))
                self.screen.blit(full_surf, full_surf.get_rect(center=(WIDTH // 2, 150)))

            if current_time - self.cheat_timer < 2000:
                cheat_surf = self.font.render("CHEAT ACTIVATED!", True, (0, 255, 100))
                self.screen.blit(cheat_surf, cheat_surf.get_rect(center=(WIDTH // 2, 200)))

            self.inventory.draw_inventory(self.screen, self.font, self.assets, self.ui)
            self.fishpedia.draw(self.screen, self.assets)
            self.shop.draw(self.screen, self.assets, self.font, self.ui, self)

            if self.show_fps:
                fps_surf = self.font.render(str(int(self.clock.get_fps())), True, (0, 255, 0))
                self.screen.blit(fps_surf, (10, 10))

    def draw(self, dt):
        dt_ms = dt * 1000

        if self.state == "menu":
            menu_surf = self.assets.get_gif_frame("menu_bg", self.assets.menu_bg_frames, dt_ms)
            self.screen.blit(pygame.transform.scale(menu_surf, (WIDTH, HEIGHT)), (0, 0))
            self.menus.draw_main_menu()

        elif self.state == "options":
            self.menus.draw_options(dt_ms)

        elif self.state == "credits":
            self.menus.draw_credits(dt_ms)

        elif self.state == "options2":
            self.menus.draw_inoptions(dt_ms)

        elif (self.state == "game" and self.menus.in_game_menu_open) or self.state == "in_menu":
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self._draw_game_scene(dt_ms)
            self.menus.draw_in_game_menu()

        elif self.state == "game":
            self._draw_game_scene(dt_ms)