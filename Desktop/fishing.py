import pygame
from settings import HEIGHT, S, top_bound, bottom_bound
from scaling import Scale


"""FISHING CLASS RESPONSIBLE FOR ROD AND BAIT MOVEMENT AND IMAGES"""

COLOR_MAP = {"default": "n", "black": "b", "pink": "p"} #Map rod color variants matching the shop 


class FishingSystem:
    def __init__(self, shop, game):
        #Fishing system will get called with 2 parameters: game and shop , to not have the 
        self.shop = shop
        self.game = game
        self.assets = game.assets

        self.tier_top_bounds = {1: 533, 2: 333, 3: 100}

        self.rod_handle_offsets = [
            pygame.Vector2(S(130), S(370)),
            pygame.Vector2(S(129), S(371)),
            pygame.Vector2(S(129), S(371)),
            pygame.Vector2(S(171), S(371)),
            pygame.Vector2(S(170), S(370)),
        ]

        self.rod_top_offsets = [
            pygame.Vector2(-S(127), -S(366)),
            pygame.Vector2(-S(81),  -S(371)),
            pygame.Vector2(0,       -S(371)),
            pygame.Vector2(S(81),   -S(371)),
            pygame.Vector2(S(127),  -S(366)),
        ]

        self.rod_pos = pygame.Vector2(S(960), HEIGHT)
        self._zone_index = 2
        self.rod_top = self.rod_pos + self.rod_top_offsets[2]

        self.bait_pos = pygame.Vector2(S(960), HEIGHT // 2)
        self.bait_vel = pygame.Vector2(0, 0)
        self.spring  = 0.1
        self.damping = 0.3
        self.speed   = 0.0

        self.bait_img = self._get_bait_img()
        self.scaler = Scale(self.bait_img)
        self._build_rod_states()
        self.rod_img = self.rod_states[2]

    def _color_key(self):
        return COLOR_MAP.get(self.shop.rod_cosmetic.get(self.shop.rod_tier, "default"), "n")

    def _build_rod_states(self):
        tier, ck = self.shop.rod_tier, self._color_key()
        self.rod_states = [self.assets.get_rod(tier, ck, o) for o in ("l", "hl", "f", "hr", "r")]

    def _get_bait_img(self):
        tier = self.shop.rod_tier
        if tier == 1:
            return self.assets.bait_1
        if tier == 2:
            return self.assets.bait_2
        color = self.shop.rod_cosmetic.get(3, "default")
        return {"default": self.assets.bait_3_n, "black": self.assets.bait_3_b, "pink": self.assets.bait_3_p}.get(color, self.assets.bait_3_n)

    def get_top_bound(self):
        return self.tier_top_bounds.get(self.shop.rod_tier, S(533))

    def get_depth(self):
        return max(0.0, min(1.0, (S(bottom_bound) - self.bait_pos.y) / (S(bottom_bound) - S(top_bound))))

    def update(self):
        self._build_rod_states()
        new_bait = self._get_bait_img()
        if new_bait is not self.bait_img:
            self.bait_img = new_bait
            self.scaler = Scale(self.bait_img)

        current_top = self.get_top_bound()
        mx, my = pygame.mouse.get_pos()
        target = pygame.Vector2(mx, max(current_top, min(S(bottom_bound), my)))

        self.bait_vel += (target - self.bait_pos) * self.spring
        self.bait_vel *= self.damping
        self.bait_pos += self.bait_vel
        self.bait_pos.y = max(current_top, min(S(bottom_bound), self.bait_pos.y))

        self._zone_index = max(0, min(4, int(self.bait_pos.x // S(384))))
        self.rod_img = self.rod_states[self._zone_index]
        self.rod_pos.x = S(960)
        self.rod_pos.y = HEIGHT
        self.rod_top = self.rod_pos + self.rod_top_offsets[self._zone_index]
        self.speed = self.bait_vel.length()

    def draw(self, screen):
        scale = 0.5 + 0.5 * ((self.bait_pos.y - S(top_bound)) / (S(bottom_bound) - S(top_bound))) * 2
        scaled_bait = self.scaler.get_scaled(scale)
        screen.blit(self.rod_img, self.rod_pos - self.rod_handle_offsets[self._zone_index])
        screen.blit(scaled_bait, scaled_bait.get_rect(center=self.bait_pos))
