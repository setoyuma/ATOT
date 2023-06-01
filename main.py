import pygame as pg, sys
from CONSTANTS import * 
from level import Level
from game_data import levels
from pygame.locals import KEYDOWN
from support import *
from scenes import *

# pg setup
class Game:
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.SCALED)
		pg.display.set_caption("ATOT")
		pg.display.set_icon(pg.image.load("./assets/logo.ico"))
		self.clock = pg.time.Clock()
		pg.mouse.set_visible(False)
		self.mouse = get_image("./assets/ui/cursor/cursor_test.png")

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", (900, 20))

	def run(self):
		while True:
			for scene in self.scenes:
				scene.update()
				scene.draw()
			self.screen.blit(self.mouse, pg.mouse.get_pos())
			self.draw_fps()
			self.send_frame()

	def send_frame(self):
		pg.display.flip()
		self.dt = self.clock.tick(FPS)/1000.0


if __name__ == '__main__':
	game = Game()
	game.scenes = [Launcher(game)]
	game.run()