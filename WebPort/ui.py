import pygame
from settings import S, WHITE

FONT_PATH = "TradeWinds-Regular.ttf"


class UI:
    def __init__(self, screen, font, game=None):
        self.screen = screen
        self.font   = font
        self.game   = game
        self._mouse_clicked  = False
        self._slider_rects   = []
        self._focus_cooldown = 0 #Frames remaining where clicks are ignored after focus gain

    def update_mouse_state(self):
        self._mouse_clicked = False #Reset each frame so clicks are only registered once
        self._slider_rects   = []
        if self._focus_cooldown > 0: #Tick down the cooldown
            self._focus_cooldown -= 1

    def register_click(self): #Call this from game.handle_events() in Game()
        if self._focus_cooldown > 0:  #Ignore clicks during cooldown so buttons can ignore phantom clicks
            return
        self._mouse_clicked = True

    def on_focus_gained(self): #Ignore 3 frames of clicks
        self._focus_cooldown = 3

    def button(self, image, image_hover, x, y, text="", text_color=WHITE, font_size=None):
        if font_size is None:
            font_size = S(35)
        mouse_pos   = pygame.mouse.get_pos()
        rect        = image.get_rect(topleft=(x, y))
        hovered     = rect.collidepoint(mouse_pos)
        over_slider = any(r.collidepoint(mouse_pos) for r in self._slider_rects)

        self.screen.blit(image_hover if hovered else image, (x, y))

        if text:
            surf = pygame.font.Font(FONT_PATH, font_size).render(text, True, text_color)
            self.screen.blit(surf, surf.get_rect(center=rect.center))

        clicked = hovered and self._mouse_clicked and not over_slider

        if clicked and self.game:
            self.game.assets.play_button()

        return clicked

    def slider(self, text, x, y, width, value, min_value, max_value,
               assets=None, show_value=False, slider_w=None, slider_h=None):
        if slider_w is None:
            slider_w = S(560)
        if slider_h is None:
            slider_h = S(110)

        mouse_pos = pygame.mouse.get_pos()
        click     = pygame.mouse.get_pressed()[0]

        bg_x = x + width // 2 - slider_w // 2
        bg_y = y - slider_h // 2 + S(6)
        hit_rect = pygame.Rect(bg_x, bg_y, slider_w, slider_h)
        self._slider_rects.append(hit_rect)

        if assets is not None:
            self.screen.blit(pygame.transform.scale(assets.button_img, (slider_w, slider_h)), (bg_x, bg_y))

        if text and text.strip():
            label = pygame.font.Font(FONT_PATH, S(22)).render(text, True, WHITE)
            self.screen.blit(label, (bg_x + S(44), bg_y + S(15)))

        pygame.draw.rect(self.screen, (220, 210, 170), pygame.Rect(x, y, width, S(12)), border_radius=S(6))

        knob_x = x + int((value - min_value) / (max_value - min_value) * width)
        pygame.draw.circle(self.screen, (80, 55, 45), (knob_x, y + S(6)), S(12))

        if show_value:
            val_surf = pygame.font.Font(FONT_PATH, S(20)).render(str(round(value, 2)), True, (80, 55, 45))
            self.screen.blit(val_surf, (bg_x + slider_w - val_surf.get_width() - S(75), bg_y + S(10)))

        if click and hit_rect.collidepoint(mouse_pos):
            value = max(min_value, min(max_value, min_value + (mouse_pos[0] - x) / width * (max_value - min_value)))


        return value
