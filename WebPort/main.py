import pygame 
import asyncio #Added asyncio , web services library
from game import Game
#Got rid of exe path finder

#Made game run on async
async def main():
    pygame.init()
    game = Game()
    await game.run() 
    pygame.quit()

asyncio.run(main()) #Calls async main() function; Creates event loop


