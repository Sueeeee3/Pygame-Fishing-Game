import pygame
import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


os.chdir(resource_path("."))

from game import Game


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()

