import pygame, sys
from settings import * 
from scenes import *

from saviorsystems.REDFORGE import *

class Game:
	def __init__(self):
		pygame.init()
		self.current_level = 2
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SCALED)
		pygame.display.set_caption("ATOT")
		pygame.display.set_icon(pygame.image.load("../assets/logo.ico"))
		self.clock = pygame.time.Clock()
		pygame.mouse.set_visible(False)
		self.mouse = get_image("../assets/ui/cursor/ValrandsCurse.png")

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", (900, 20))

	def run(self):
		while True:
			for scene in self.scenes:
				scene.update()
				scene.draw()
			self.screen.blit(self.mouse, pygame.mouse.get_pos())
			self.draw_fps()
			self.send_frame()

	def send_frame(self):
		pygame.display.flip()
		self.dt = self.clock.tick(FPS)/1000.0


if __name__ == '__main__':
	game = Game()
	game.scenes = [Launcher(game)]
	game.run()