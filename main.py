import pygame as pg
import sys
from world import World
from world_data import worlds
from settings import *

class Game:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pg.display.set_caption("Song Of Valks")
        self.clock = pg.time.Clock()
        self.FPS = 60
        self.running = True
        self.world = World(worlds[1], self.screen)


    def run(self):
        while self.running:
            self.screen.fill("gray")
            
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    print("Game Closed")
                    self.running = False
                    pg.quit()
                    sys.exit()
             
            self.world.run()
            self.clock.tick(60)
            pg.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()
