import pygame


class Scale:
    def __init__(self, original_image):
        self.original = original_image
        self.cache = {}

    def get_scaled(self, scale, smooth=True):
        key = round(scale, 2)
        if key not in self.cache:
            w = int(self.original.get_width() * key)
            h = int(self.original.get_height() * key)
            transform = pygame.transform.smoothscale if smooth else pygame.transform.scale
            self.cache[key] = transform(self.original, (w, h))
        return self.cache[key]