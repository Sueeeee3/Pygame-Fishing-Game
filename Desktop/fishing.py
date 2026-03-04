import pygame
from settings import HEIGHT, S, top_bound, bottom_bound
from scaling import Scale


"""
FishingSystem Class- manages fishing rod and bait.

Handles:
-Rod image selection based on screen zone (5 orientations) and shop tier/colour
-Bait movement physics towards mouse in bounds based on rod tier
-Depth and speed calculations consumed by Game() for rope and fish scare logic
"""

COLOR_MAP = {"default": "n", "black": "b", "pink": "p"} #Maps shop cosmetic names to corresponding asset suffix letters

class FishingSystem:
    def __init__(self, shop, game):
        #Accepts Game and Shop instances directly (Avoiding circular imports)
        self.shop = shop
        self.game = game
        self.assets = game.assets #Use Assets dependency from Game() 
        
        #Y-axis bait position bounds at the top, dependant on rod tier  
        self.tier_top_bounds = {1: 533, 2: 333, 3: 100}
        
        #Pixel offset to align all 5 rod orientations so handle has correct, non changing position on screen
        #Ordered: Left, Half-Left, Front, Half-Right, Right
        self.rod_handle_offsets = [ 
            pygame.Vector2(130, 370),
            pygame.Vector2(129, 371),
            pygame.Vector2(129, 371),
            pygame.Vector2(171, 371),
            pygame.Vector2(170, 370),
        ]
        #The same, just with rod top; used in Rope() as rope starting point
        self.rod_top_offsets = [
            pygame.Vector2(127, 366),
            pygame.Vector2(81,  371),
            pygame.Vector2(0,  -371),
            pygame.Vector2(81, -371),
            pygame.Vector2(127,-366),
        ]

        self.rod_pos = pygame.Vector2(960, HEIGHT) #Rod starts centered
        self._zone_index = 2 #Current zone (0-4); Used to decide what rod orientation image would be used; Start with zone 2 (front)
        self.rod_top = self.rod_pos + self.rod_top_offsets[2] 
        
        self.bait_pos = pygame.Vector2(960, HEIGHT // 2) #Bait start centered, above rod
        self.bait_vel = pygame.Vector2(0, 0) #Empty Bait velocity vector used later
        
        self.spring  = 0.1 #Pulls bait towards target
        self.damping = 0.3 #Prevents oscilation, gives resistance
        self.speed   = 0.0 #Speed, used later by Game() for fish scare event if splash approached too fast

       
        self.bait_img = self._get_bait_img() #Getting current bait image with _get_bait method
        self.scaler = Scale(self.bait_img) #Establishing instance of Scale() which resizes the image
        self._build_rod_states() #Calling method (line 67)
        self.rod_img = self.rod_states[2] #Call rod image correspondign to front position

    def _color_key(self): 
        #Looks up current rod tier cosmetic choice from Shop() and maps corresponding asset suffix
        return COLOR_MAP.get(self.shop.rod_cosmetic.get(self.shop.rod_tier, "default"), "n") 

    def _build_rod_states(self):
        #Loads all 5 orientation sprites for the current tier and colour into a list, indexed by orientation (zone)
        tier, ck = self.shop.rod_tier, self._color_key()
        self.rod_states = [self.assets.get_rod(tier, ck, o) for o in ("l", "hl", "f", "hr", "r")]

    def _get_bait_img(self): 
        #Tier 1 and 2 have single bait sprite; Tier 3 has colour variants matching rod cosmetic
        tier = self.shop.rod_tier
        if tier == 1:
            return self.assets.bait_1
        if tier == 2:
            return self.assets.bait_2
        color = self.shop.rod_cosmetic.get(3, "default")
        return {"default": self.assets.bait_3_n, "black": self.assets.bait_3_b, "pink": self.assets.bait_3_p}.get(color, self.assets.bait_3_n) 

    def get_top_bound(self): 
        #Returns upper Y-axis limit (bound) for bait movement, based on rod tiers; Defaults to Tier 1
        return self.tier_top_bounds.get(self.shop.rod_tier, 533)

    def get_depth(self): 
        #Calculate bait-Y as [0.0;1.0] depth value, used in Game() class for rope
        return max(0.0, min(1.0, (bottom_bound - self.bait_pos.y) / (bottom_bound - top_bound)))

    def update(self): 
        self._build_rod_states()

        #Swap bait sprite and rebuild scaler only when the tier or cosmetic has changed
        new_bait = self._get_bait_img()
        if new_bait is not self.bait_img:
            self.bait_img = new_bait
            self.scaler = Scale(self.bait_img)

        current_top = self.get_top_bound() 
        mx, my = pygame.mouse.get_pos() #Gettting current mouse position
        target = pygame.Vector2(mx, max(current_top, min(bottom_bound, my)))#Bind mouse Y-axis to valid range

        #Physics calculations; Accelerate toward targert, damp to settle smoothly
        self.bait_vel += (target - self.bait_pos) * self.spring 
        self.bait_vel *= self.damping
        self.bait_pos += self.bait_vel 
        self.bait_pos.y = max(current_top, min(bottom_bound, self.bait_pos.y)) #Bind bait position to fit valid area in case velocity pushed it out of bounds

        #Divide screen into 5 equal zones to pick correct rod orientation
        self._zone_index = max(0, min(4, int(self.bait_pos.x // 384))) 
        self.rod_img = self.rod_states[self._zone_index] 
        
        self.rod_pos.x = 960 
        self.rod_pos.y = HEIGHT 
        self.rod_top = self.rod_pos + self.rod_top_offsets[self._zone_index]

        #Use bait velocity vector lenght to set a speed scalar used by Game()
        self.speed = self.bait_vel.length()

    def draw(self, screen):
        #Scale bait image to fake having a perspective
        scale = 0.5 + 0.5 * ((self.bait_pos.y - (((top_bound / bottom_bound) - top_bound)) * 2 
        scaled_bait = self.scaler.get_scaled(scale) 
        #Draw rod and bait; Rod with correct zone offset; Bait uses scaled image (get_rect(center=..) is to make sure its centered
        screen.blit(self.rod_img, self.rod_pos - self.rod_handle_offsets[self._zone_index])  
        screen.blit(scaled_bait, scaled_bait.get_rect(center=self.bait_pos))


