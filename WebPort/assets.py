import pygame
#PIL not supported on web build so GIF frames are pre-extracted into folders and loaded manually
#Removed numpy and distorted voice effect (Not supported on web); Voice saved locally as snd_type_2
#All sounds converted to ogg for web compatibility
#All assets scaled using S() so they respond to resolution change


from settings import WIDTH, HEIGHT, SCALE, S

def _load_gif(folder, speed_mult=1.0, target_size=None): 
    #Loads pre-extracted GIF frames and their durations from a folder
    #speed_mult scales all frame durations to speed up or slow down the animation
    frames = []
    with open(f"{folder}/durations.txt") as f:
        durations = [int(x) for x in f.read().splitlines()]
    for i, dur in enumerate(durations):
        surf = pygame.image.load(f"{folder}/frame_{i:04d}.png").convert_alpha()
        if target_size:
            surf = pygame.transform.scale(surf, target_size)
        frames.append((surf, int(dur * speed_mult)))
    return frames

class Assets:
    def __init__(self):
        self.options_bg_frames = _load_gif("assets/options_background", target_size=(WIDTH, HEIGHT))
        self.lake_frames       = _load_gif("assets/game_water", speed_mult=3.0, target_size=(WIDTH, HEIGHT))
        self.menu_bg_frames    = _load_gif("assets/menu_bg", target_size=(WIDTH, HEIGHT))

        self.inventory_bg = pygame.transform.scale(pygame.image.load("assets/inventory_bg.png"), (WIDTH, HEIGHT))
        self.gui          = pygame.transform.scale(pygame.image.load("assets/gui.png").convert_alpha(), (S(1750), S(350)))
        self.shop_bg      = pygame.transform.scale(pygame.image.load("assets/shop_bg.png"), (WIDTH, HEIGHT))
        self.dock         = pygame.transform.scale(pygame.image.load("assets/dock.png").convert_alpha(), (S(1920), S(1080)))

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
            img = pygame.image.load(f"assets/{filename}.png").convert_alpha()
            orig_w, orig_h = img.get_size()
            setattr(self, attr, pygame.transform.scale(img, (S(orig_w), S(orig_h))))

        self.button_img       = pygame.transform.scale(pygame.image.load("assets/button_normal.png").convert_alpha(), (S(1750), S(350)))
        self.button_hover_img = pygame.transform.scale(pygame.image.load("assets/button_hover.png").convert_alpha(), (S(1750), S(350)))

        self.splash_frames = _load_gif("assets/splash", target_size=(S(250), S(250)))
        self.splash_img    = self.splash_frames[0][0]

        self.line  = pygame.transform.scale(pygame.image.load("assets/line.png").convert_alpha(), (S(160), S(88)))
        self.red   = pygame.transform.scale(pygame.image.load("assets/red.png"), (S(90), S(760)))
        self.green = pygame.transform.scale(pygame.image.load("assets/green.png").convert_alpha(), (S(80), S(80)))

        self.worm  = pygame.transform.scale(pygame.image.load("assets/worm.png").convert_alpha(), (S(100), S(100)))
        self.bread = pygame.transform.scale(pygame.image.load("assets/bread.png").convert_alpha(), (S(100), S(100)))
        self.prof  = pygame.transform.scale(pygame.image.load("assets/prof_bait.png").convert_alpha(), (S(100), S(100)))

        self.bait_1   = pygame.transform.scale(pygame.image.load("assets/b_1.png").convert_alpha(), (S(50), S(50)))
        self.bait_2   = pygame.transform.scale(pygame.image.load("assets/b_2.png").convert_alpha(), (S(50), S(50)))
        self.bait_3_n = pygame.transform.scale(pygame.image.load("assets/b_3_n.png").convert_alpha(), (S(50), S(50)))
        self.bait_3_p = pygame.transform.scale(pygame.image.load("assets/b_3_p.png").convert_alpha(), (S(50), S(50)))
        self.bait_3_b = pygame.transform.scale(pygame.image.load("assets/b_3_b.png").convert_alpha(), (S(50), S(50)))

        pygame.mixer.set_num_channels(16)

        self.snd_ambient      = pygame.mixer.Sound("assets/Sounds/ambient.ogg")
        self.snd_options      = pygame.mixer.Sound("assets/Sounds/options.ogg")
        self.snd_fail         = pygame.mixer.Sound("assets/Sounds/Faliure.ogg")
        self.snd_success      = pygame.mixer.Sound("assets/Sounds/Succes.ogg")
        self.snd_reel         = pygame.mixer.Sound("assets/Sounds/Reel.ogg")
        self.snd_splash       = pygame.mixer.Sound("assets/Sounds/splash.ogg")
        self.snd_button       = pygame.mixer.Sound("assets/Sounds/button.ogg")
        self.snd_type         = pygame.mixer.Sound("assets/Sounds/aa.ogg")
        self.snd_type_2       = pygame.mixer.Sound("assets/Sounds/bb.ogg")
        self.snd_inventory    = pygame.mixer.Sound("assets/Sounds/ice.ogg")
        self.snd_shop         = pygame.mixer.Sound("assets/Sounds/bell.ogg")
        self.snd_fishpedia    = pygame.mixer.Sound("assets/Sounds/page.ogg")

        self._base_vol = {
            "ambient":      0.55,
            "options":      0.65,
            "type":         0.65,
            "type_2":       0.65,
            "button":       0.75,
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
        self.snd_type_2.set_volume(self._base_vol["type_2"])
        self.snd_button.set_volume(self._base_vol["button"])
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
                img = pygame.image.load(f"assets/{prefix}_{suffix}.png").convert_alpha()
                orig_w, orig_h = img.get_size()
                setattr(self, f"{attr_prefix}_{attr_suffix}",
                        pygame.transform.scale(img, (S(orig_w), S(orig_h))))

        self.rods = {}
        for tier in (1, 2, 3):
            for color in ("n", "b", "p"):
                for orient in ("l", "hl", "f", "hr", "r"):
                    img = pygame.image.load(f"assets/r_{tier}_{color}_{orient}.png").convert_alpha()
                    if orient in ("hr", "r"):
                        img = pygame.transform.flip(img, True, False)
                    orig_w, orig_h = img.get_size()
                    self.rods[(tier, color, orient)] = pygame.transform.scale(img, (S(orig_w), S(orig_h)))

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
        self.snd_type_2.set_volume(self._base_vol["type_2"] * self._music_vol)
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
            self.CH_TYPE.play(self.snd_type_2)

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



