import pygame
import sys
import ctypes
from settings import *

FONT_PATH = "TradeWinds-Regular.ttf"


def set_mouse_sensitivity(level):
    windows_level = max(1, min(20, int(1 + (level - 0.1) / (5.0 - 0.1) * 19)))
    ctypes.windll.user32.SystemParametersInfoW(0x0071, 0, windows_level, 0)


class Menus:
    def __init__(self, game):
        self.game               = game
        self.fullscreen         = True
        self.screen             = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
        self.font               = game.font
        self.clock              = game.clock
        self.ui                 = game.ui
        self.in_game_menu_open  = False

    def _btn(self, w, h):
        return pygame.transform.scale(self.game.assets.button_img, (w, h))

    def _btnh(self, w, h):
        return pygame.transform.scale(self.game.assets.button_hover_img, (w, h))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.game.screen = pygame.display.set_mode(
            WINDOW_SIZE, pygame.FULLSCREEN if self.fullscreen else 0
        )
        self.screen = self.game.screen

    def draw_main_menu(self):
        pygame.mouse.set_visible(True)
        bw, bh = 560, 110
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)

        if self.ui.button(btn, btnh, 110, 620, "New Game"):
            self.game.new_game()

        if self.game.save_system.has_save():
            if self.ui.button(btn, btnh, 110, 750, "Continue"):
                if self.game.save_system.load(self.game):
                    self.game.state = "game"
        else:
            grey = self._btn(bw, bh).copy()
            grey.set_alpha(100)
            self.screen.blit(grey, (110, 750))
            cant = pygame.font.Font(FONT_PATH, 35).render("Continue", True, (120, 120, 120))
            self.screen.blit(cant, cant.get_rect(center=(110 + bw // 2, 750 + bh // 2)))

        if self.ui.button(btn, btnh, 110, 880, "Options"):
            self.game.state = "options"

        quit_bw, quit_bh = 300, 90
        if self.ui.button(self._btn(quit_bw, quit_bh), self._btnh(quit_bw, quit_bh), 1580, 940, "Quit"):
            pygame.quit()
            sys.exit()

    def _draw_options_bg(self, dt_ms):
        surf = self.game.assets.get_gif_frame("options_bg", self.game.assets.options_bg_frames, dt_ms)
        self.screen.blit(pygame.transform.scale(surf, WINDOW_SIZE), (0, 0))

    def _draw_sensitivity_and_volume(self, cx, vol_y, sens_y):
        self.game.music_volume = self.ui.slider(
            "Music Volume", cx - 200, vol_y, 400,
            self.game.music_volume, 0.0, 1.0,
            assets=self.game.assets, show_value=True
        )

        old_sens = self.game.mouse_sensitivity
        self.game.mouse_sensitivity = self.ui.slider(
            "Mouse Sensitivity", cx - 200, sens_y, 400,
            self.game.mouse_sensitivity, 0.1, 5.0,
            assets=self.game.assets, show_value=True
        )
        if self.game.mouse_sensitivity != old_sens:
            set_mouse_sensitivity(self.game.mouse_sensitivity)

    def draw_options(self, dt_ms=0):
        self._draw_options_bg(dt_ms)
        cx    = WINDOW_SIZE[0] // 2
        bw, bh = 560, 110
        btn_x  = cx - bw // 2
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)

        if self.ui.button(btn, btnh, btn_x, 180, "Toggle Fullscreen"):
            self.toggle_fullscreen()

        self._draw_sensitivity_and_volume(cx, 410, 590)

        if self.ui.button(btn, btnh, btn_x, 730, "Credits"):
            self.game.state = "credits"
        if self.ui.button(btn, btnh, btn_x, 860, "Back"):
            self.game.state = "menu"

    def draw_credits(self, dt_ms=0):
        self._draw_options_bg(dt_ms)
        dark = pygame.Surface(WINDOW_SIZE)
        dark.set_alpha(120)
        dark.fill((0, 0, 0))
        self.screen.blit(dark, (0, 0))

        small_font = pygame.font.Font(FONT_PATH, 18)

        credits_data = [
            (self.font,  "Worst Fishing Game EVER"),
            (self.font,  "Created by: Sue"),
            (self.font,  "Graphics: Sue"),
            (self.font,  "Music From FreeSound.org:"),
            (small_font, "FunWithSound: Success Fanfare Trumpets.mp3"),
            (small_font, "sweet_niche: Trumpet_Cry.wav"),
            (small_font, "richwise: Waterside, foggy morning"),
            (small_font, "Jay_You: music elevator ext part 1/3"),
            (small_font, "paulprit: Angel Fly Fish Reel Slow Pull_1.wav"),
            (small_font, "Robinhood76: 05966 water surfacing splashes.wav"),
            (small_font, "Duisterwho: Awesome man - vocal"),
            (small_font, "AlienXXX: Tearing_rotten_wood_5a.wav"),
            (small_font, "NachtmahrTV: Shop Bell"),
            (small_font, "IENBA: Page Turn"),
            (small_font, "Omiranda14: SFX_Spell_IceShoot_02"),
            (self.font,  "Thanks for playing <3!"),
        ]

        y = 80
        for font, line in credits_data:
            surf = font.render(line, True, WHITE)
            self.screen.blit(surf, (100, y))
            y += font.get_height() + 10

        bw, bh = 560, 110
        if self.ui.button(self._btn(bw, bh), self._btnh(bw, bh), 150, WINDOW_SIZE[1] - 200, "Back"):
            self.game.state = "options"
        pygame.display.flip()

    def draw_inoptions(self, dt_ms=0):
        self._draw_options_bg(dt_ms)
        cx    = WINDOW_SIZE[0] // 2
        bw, bh = 560, 110
        btn_x  = cx - bw // 2

        self._draw_sensitivity_and_volume(cx, 390, 570)

        if self.ui.button(self._btn(bw, bh), self._btnh(bw, bh), btn_x, 720, "Back"):
            self.game.state        = "in_menu"
            self.in_game_menu_open = True
        pygame.display.flip()

    def draw_in_game_menu(self):
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        bw, bh  = 560, 110
        btn, btnh = self._btn(bw, bh), self._btnh(bw, bh)
        menu_x  = int(WINDOW_SIZE[0] * 0.355)
        start_y = int(WINDOW_SIZE[1] * 0.355)
        gap     = 20

        if self.ui.button(btn, btnh, menu_x, start_y, "Continue"):
            self.in_game_menu_open = False
            self.game.state        = "game"

        if self.ui.button(btn, btnh, menu_x, start_y + bh + gap, "Options"):
            self.game.state        = "options2"
            self.in_game_menu_open = False

        if self.ui.button(btn, btnh, menu_x, start_y + 2 * (bh + gap), "Quit to Menu"):
            self.game.assets.stop_reel()
            self.game.splashes.clear(self.game.assets)
            self.game.save_system.save(self.game)
            self.game.state        = "menu"
            self.in_game_menu_open = False