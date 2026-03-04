import pygame
from PIL import Image as PilImage


def _load_gif(path, speed_mult=1.0):
    pil = PilImage.open(path)
    frames = []
    try:
        while True:
            duration = pil.info.get("duration", 100)
            surf = pygame.image.fromstring(
                pil.convert("RGBA").tobytes(), pil.size, "RGBA"
            ).convert_alpha()
            frames.append((surf, int(duration * speed_mult)))
            pil.seek(pil.tell() + 1)
    except EOFError:
        pass
    return frames


def _distort_sound(sound, pitch=0.65, crackle=0.35):
    import numpy as np
    pygame.mixer.get_init()
    raw = pygame.sndarray.array(sound).copy().astype(np.float32)
    raw /= 32768.0

    factor    = 1.0 / pitch
    out_len   = int(len(raw) * factor)
    indices   = np.clip((np.arange(out_len) / factor).astype(int), 0, len(raw) - 1)
    stretched = raw[indices]

    kernel = 5
    if stretched.ndim == 2:
        for ch in range(stretched.shape[1]):
            stretched[:, ch] = np.convolve(stretched[:, ch], np.ones(kernel) / kernel, mode="same")
    else:
        stretched = np.convolve(stretched, np.ones(kernel) / kernel, mode="same")

    stretched = np.tanh(stretched * (1.5 + crackle * 2.5))
    limit     = 1.0 - crackle * 0.3
    stretched = np.clip(stretched, -limit, limit)

    presence  = 0.15
    diff      = np.diff(stretched, axis=0, prepend=stretched[:1] if stretched.ndim == 2 else stretched[:1])
    stretched = stretched + presence * diff

    peak = np.abs(stretched).max()
    if peak > 0:
        stretched = stretched / peak * 0.90
    return pygame.sndarray.make_sound((stretched * 32767).astype(np.int16))


class Assets:
    def __init__(self):
        self.options_bg_frames = _load_gif("assets/options_background.gif")
        self.lake_frames       = _load_gif("assets/game_water.gif", speed_mult=3.0)
        self.menu_bg_frames    = _load_gif("assets/menu_bg.gif")

        self.inventory_bg = pygame.image.load("assets/inventory_bg.png")
        self.gui          = pygame.image.load("assets/gui.png").convert_alpha()
        self.shop_bg      = pygame.image.load("assets/shop_bg.png")
        self.dock         = pygame.image.load("assets/dock.png").convert_alpha()

        fish_assets = [
            "japanesefish", "filletfish", "fishbone", "selfish", "fish_scale",
            "smallfish", "tunacan", "swedish", "starfish", "silverfish",
            "jellyfish", "fishtaco", "fishtank", "fishstick", "fishschool",
            "fishsauce", "fishnet", "fishcracer", "fishandchips", "catfish",
        ]
        attr_names = [
            "taiyaki", "fillet", "fishbone", "selfish", "fish_scale",
            "small", "tuna", "swedish", "starfish", "silverfish",
            "jellyfish", "taco", "fishtank", "stick", "fishschool",
            "sauce", "fishnet", "cracker", "fishandchips", "catfish",
        ]
        for attr, filename in zip(attr_names, fish_assets):
            setattr(self, attr, pygame.image.load(f"assets/{filename}.png").convert_alpha())

        self.button_img       = pygame.image.load("assets/button_normal.png").convert_alpha()
        self.button_hover_img = pygame.image.load("assets/button_hover.png").convert_alpha()

        self.splash_frames = _load_gif("assets/splash.gif")
        self.splash_img    = self.splash_frames[0][0]

        self.line  = pygame.image.load("assets/line.png").convert_alpha()
        self.red   = pygame.image.load("assets/red.png")
        self.green = pygame.image.load("assets/green.png").convert_alpha()

        self.worm  = pygame.image.load("assets/worm.png").convert_alpha()
        self.bread = pygame.image.load("assets/bread.png").convert_alpha()
        self.prof  = pygame.image.load("assets/prof_bait.png").convert_alpha()

        self.bait_1   = pygame.image.load("assets/b_1.png").convert_alpha()
        self.bait_2   = pygame.image.load("assets/b_2.png").convert_alpha()
        self.bait_3_n = pygame.image.load("assets/b_3_n.png").convert_alpha()
        self.bait_3_p = pygame.image.load("assets/b_3_p.png").convert_alpha()
        self.bait_3_b = pygame.image.load("assets/b_3_b.png").convert_alpha()

        pygame.mixer.set_num_channels(16)

        self.snd_ambient   = pygame.mixer.Sound("assets/Sounds/ambient.wav")
        self.snd_options   = pygame.mixer.Sound("assets/Sounds/options.wav")
        self.snd_fail      = pygame.mixer.Sound("assets/Sounds/Faliure.wav")
        self.snd_success   = pygame.mixer.Sound("assets/Sounds/Succes.wav")
        self.snd_reel      = pygame.mixer.Sound("assets/Sounds/Reel.wav")
        self.snd_splash    = pygame.mixer.Sound("assets/Sounds/splash.wav")
        self.snd_button    = pygame.mixer.Sound("assets/Sounds/button.wav")
        self.snd_type      = pygame.mixer.Sound("assets/Sounds/aa.wav")
        self.snd_inventory = pygame.mixer.Sound("assets/Sounds/ice.wav")
        self.snd_shop      = pygame.mixer.Sound("assets/Sounds/bell.wav")
        self.snd_fishpedia = pygame.mixer.Sound("assets/Sounds/page.wav")

        try:
            raw_voice = pygame.mixer.Sound("assets/Sounds/voice.wav")
        except Exception:
            raw_voice = self.snd_type
        self.snd_police_voice = _distort_sound(raw_voice, pitch=0.78, crackle=0.18)

        self._base_vol = {
            "ambient":      0.55,
            "options":      0.65,
            "type":         0.65,
            "button":       0.75,
            "police_voice": 0.70,
            "splash":       0.40,
            "reel":         1.00,
            "ui":           1.00,
            "success":      1.00,
            "fail":         1.00,
        }

        self._music_vol    = 1.0
        self._current_snd  = None
        self._music_active = None
        self._fading       = False
        self._fade_timer   = 0.0
        self._fade_dur     = 1.2

        self.snd_ambient.set_volume(self._base_vol["ambient"])
        self.snd_options.set_volume(self._base_vol["options"])
        self.snd_type.set_volume(self._base_vol["type"])
        self.snd_button.set_volume(self._base_vol["button"])
        self.snd_police_voice.set_volume(self._base_vol["police_voice"])
        self.snd_splash.set_volume(self._base_vol["splash"])

        pygame.mixer.set_reserved(5)

        self.CH_MUSIC_A = pygame.mixer.Channel(0)
        self.CH_MUSIC_B = pygame.mixer.Channel(1)
        self.CH_REEL    = pygame.mixer.Channel(2)
        self.CH_TYPE    = pygame.mixer.Channel(3)
        self.CH_UI      = pygame.mixer.Channel(4)
        self.CH_SPLASH  = pygame.mixer.Channel(5)
        pygame.mixer.set_reserved(6)

        for tier, prefix, attr_prefix in [(1, "t1", "c"), (2, "t2", "b"), (3, "t3", "f")]:
            for suffix, attr_suffix in [("e", "e"), ("h", "h"), ("f", "f")]:
                setattr(self, f"{attr_prefix}_{attr_suffix}",
                        pygame.image.load(f"assets/{prefix}_{suffix}.png").convert_alpha())

        self.rods = {}
        for tier in (1, 2, 3):
            for color in ("n", "b", "p"):
                for orient in ("l", "hl", "f", "hr", "r"):
                    img = pygame.image.load(f"assets/r_{tier}_{color}_{orient}.png").convert_alpha()
                    if orient in ("hr", "r"):
                        img = pygame.transform.flip(img, True, False)
                    self.rods[(tier, color, orient)] = img

        self.rod_f      = self.rods[(1, "n", "f")]
        self.gif_timers = {}
        self.gif_index  = {}

    def set_music_volume(self, vol):
        self._music_vol = max(0.0, min(1.0, vol))

        if self._music_active == "A":
            self.CH_MUSIC_A.set_volume(self._music_vol)
        elif self._music_active == "B":
            self.CH_MUSIC_B.set_volume(self._music_vol)

        self.CH_UI.set_volume(self._base_vol["ui"] * self._music_vol)
        self.CH_REEL.set_volume(self._base_vol["reel"] * self._music_vol)
        self.CH_SPLASH.set_volume(self._base_vol["splash"] * self._music_vol)

        self.snd_ambient.set_volume(self._base_vol["ambient"] * self._music_vol)
        self.snd_options.set_volume(self._base_vol["options"] * self._music_vol)
        self.snd_button.set_volume(self._base_vol["button"] * self._music_vol)
        self.snd_type.set_volume(self._base_vol["type"] * self._music_vol)
        self.snd_police_voice.set_volume(self._base_vol["police_voice"] * self._music_vol)
        self.snd_splash.set_volume(self._base_vol["splash"] * self._music_vol)
        self.snd_success.set_volume(self._base_vol["success"] * self._music_vol)
        self.snd_fail.set_volume(self._base_vol["fail"] * self._music_vol)
        self.snd_inventory.set_volume(self._base_vol["ui"] * self._music_vol)
        self.snd_shop.set_volume(self._base_vol["ui"] * self._music_vol)
        self.snd_fishpedia.set_volume(self._base_vol["ui"] * self._music_vol)

    def pause_all(self):
        pygame.mixer.pause()

    def resume_all(self):
        pygame.mixer.unpause()

    def play_music(self, sound):
        if sound is self._current_snd:
            ch = self.CH_MUSIC_A if self._music_active == "A" else self.CH_MUSIC_B
            if ch is not None and not ch.get_busy():
                ch.set_volume(self._music_vol)
                ch.play(sound, loops=-1)
            return

        self._current_snd  = sound
        self._fading       = True
        self._fade_timer   = 0.0

        if self._music_active != "B":
            incoming_ch        = self.CH_MUSIC_B
            self._music_active = "B"
        else:
            incoming_ch        = self.CH_MUSIC_A
            self._music_active = "A"

        incoming_ch.set_volume(0.0)
        incoming_ch.play(sound, loops=-1)

    def stop_music(self):
        self.CH_MUSIC_A.stop()
        self.CH_MUSIC_B.stop()
        self._current_snd  = None
        self._music_active = None
        self._fading       = False

    def update_music(self, dt):
        if not self._fading:
            return
        self._fade_timer += dt
        t = min(self._fade_timer / self._fade_dur, 1.0)

        if self._music_active == "B":
            self.CH_MUSIC_B.set_volume(self._music_vol * t)
            self.CH_MUSIC_A.set_volume(self._music_vol * (1.0 - t))
        else:
            self.CH_MUSIC_A.set_volume(self._music_vol * t)
            self.CH_MUSIC_B.set_volume(self._music_vol * (1.0 - t))

        if t >= 1.0:
            self._fading = False
            if self._music_active == "B":
                self.CH_MUSIC_A.stop()
            else:
                self.CH_MUSIC_B.stop()

    def play_reel(self):
        if not self.CH_REEL.get_busy():
            self.CH_REEL.play(self.snd_reel, loops=-1)

    def stop_reel(self):
        self.CH_REEL.stop()

    def _free_channel(self):
        for i in range(6, 16):
            ch = pygame.mixer.Channel(i)
            if not ch.get_busy():
                return ch
        return pygame.mixer.Channel(6)

    def play_button(self):
        self.CH_UI.play(self.snd_button)

    def play_type(self):
        if not self.CH_TYPE.get_busy():
            self.CH_TYPE.play(self.snd_type)

    def play_police_type(self):
        if not self.CH_TYPE.get_busy():
            self.CH_TYPE.play(self.snd_police_voice)

    def play_success(self):
        self._free_channel().play(self.snd_success)

    def play_fail(self):
        self._free_channel().play(self.snd_fail)

    def play_splash(self):
        self.CH_SPLASH.play(self.snd_splash)

    def stop_splash(self):
        self.CH_SPLASH.stop()

    def play_ui(self, sound):
        self.CH_UI.play(sound)

    def get_rod(self, tier, color, orient):
        return self.rods[(tier, color, orient)]

    def get_gif_frame(self, name, frames, dt_ms):
        if name not in self.gif_index:
            self.gif_index[name]  = 0
            self.gif_timers[name] = 0

        self.gif_timers[name] += dt_ms
        surf, duration = frames[self.gif_index[name]]
        if self.gif_timers[name] >= duration:
            self.gif_timers[name] -= duration
            self.gif_index[name]   = (self.gif_index[name] + 1) % len(frames)
            surf, _ = frames[self.gif_index[name]]
        return surf

    def get_splash_frame_at(self, elapsed_ms, total_ms, frames):
        if not frames or total_ms <= 0:
            return frames[0][0]
        t     = max(0.0, min(1.0, elapsed_ms / total_ms))
        index = min(int(t * len(frames)), len(frames) - 1)
        return frames[index][0]