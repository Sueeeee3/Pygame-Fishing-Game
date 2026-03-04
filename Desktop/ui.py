import pygame

FONT_PATH = "TradeWinds-Regular.ttf"

"""
Ui- responsible for buttons and sliders

Handles:
-Drawing buttons and sliders
-Mouse click detection 
-Game() is passed in so buttons can trigger sound effects
"""

class UI:
    def __init__(self, screen, font, game=None):
        self.screen = screen
        self.font   = font
        #Accepts Game instance directly (Avoiding circular import)
        self.game   = game
        self._mouse_was_down = False #Tracks previous frame mouse state to detect fresh clicks 
        self._slider_rects   = [] #List of slider areas; Buttons won't register click if the mouse is over any of them

    def update_mouse_state(self):
        self._mouse_was_down = pygame.mouse.get_pressed()[0] #Save mouse state before next frame
        self._slider_rects   = []  #Rebuild each frame since sliders may move or disappear

    def button(self, image, image_hover, x, y, text="", text_color=(255, 255, 255), font_size=50): 
        #Define and draw button
      
        #Get mouse position and if it was clicked or not
        mouse_pos  = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
      
        #Create a rectangle (hitbox) same size as button and check if mouse is colliding with it
        rect       = image.get_rect(topleft=(x, y))
        hovered    = rect.collidepoint(mouse_pos)
      
        over_slider = any(r.collidepoint(mouse_pos) for r in self._slider_rects) #Buttons don't register clicks if hidden under sliders

        #Draw hovered image if they collide
        self.screen.blit(image_hover if hovered else image, (x, y))

        #If text was passed in render it and draw it centred on the button
        if text:
            surf = pygame.font.Font(FONT_PATH, font_size).render(text, True, text_color)
            self.screen.blit(surf, surf.get_rect(center=rect.center))

        clicked = hovered and mouse_down and not self._mouse_was_down and not over_slider #Check if button was clicked (Only true on the first frame of the click)
        if clicked and self.game:
            self.game.assets.play_button()

        return clicked

    def slider(self, text, x, y, width, value, min_value, max_value,
               assets=None, show_value=False, slider_w=560, slider_h=110):
        #Define and draw slider

        #Get mouse position and if it was clicked or not
        mouse_pos = pygame.mouse.get_pos()
        click     = pygame.mouse.get_pressed()[0]

        bg_x = x + width // 2 - slider_w // 2 #Centre background panel over the track
        bg_y = y - slider_h // 2 + 6

        #Create a rectangle (hitbox) same size as slider background
        hit_rect = pygame.Rect(bg_x, bg_y, slider_w, slider_h)
        self._slider_rects.append(hit_rect) #Register hit rect so buttons underneath won't fire while dragging

        if assets is not None:
            #Draw background if given
            self.screen.blit(pygame.transform.scale(assets.button_img, (slider_w, slider_h)), (bg_x, bg_y))

        if text and text.strip():
            #If text was passed in render it and draw it in a label
            label = pygame.font.Font(FONT_PATH, 22).render(text, True, (255, 255, 255))
            self.screen.blit(label, (bg_x + 44, bg_y + 15))

        pygame.draw.rect(self.screen, (220, 210, 170), pygame.Rect(x, y, width, 12), border_radius=6) #Draws the slider track
        knob_x = x + int((value - min_value) / (max_value - min_value) * width) #Convert value to knob position on track
        pygame.draw.circle(self.screen, (80, 55, 45), (knob_x, y + 6), 12) #Draws the knob

        if show_value:
            #Render current value as text in top right of slider background
            val_surf = pygame.font.Font(FONT_PATH, 20).render(str(round(value, 2)), True, (80, 55, 45))
            self.screen.blit(val_surf, (bg_x + slider_w - val_surf.get_width() - 75, bg_y + 10))

        if click and hit_rect.collidepoint(mouse_pos):
            #Updates the value when the slider is clicked; Converts mouse x pos into a value, clamped to range
            value = max(min_value, min(max_value, min_value + (mouse_pos[0] - x) / width * (max_value - min_value)))

        return value
