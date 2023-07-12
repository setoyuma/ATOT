import random
import time
from math import sin

from scenes import *
from utils import *


class Game:

	def __init__(self):
		self.setup_pygame()
		self.setup_world()
		self.show_fps = False
		self.font = import_cut_graphics('../assets/ui/menu/ATOT_Alphabet.png', 16)

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("A Tale Of Time")
		pygame.display.set_icon(get_image('../assets/logo.ico'))
		pygame.mixer.init()
		pygame.mouse.set_visible(False)
		self.mx, self.my = pygame.mouse.get_pos()

	def setup_world(self):
		self.current_world = 'church_of_melara'
		self.world = World(self, WORLDS[self.current_world]['csv'])

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"fps: {fpsCounter}", [900, 20], font=FONT, size=42)

	def send_frame(self):
		pygame.display.flip()
		self.clock.tick(FPS)

	def run(self):
		self.running = True
		self.last_time = time.time()
		while self.running:
			self.mx, self.my = pygame.mouse.get_pos()
			self.cursor = Cursor(self, 'ValrandsCurse', 64)
			self.dt = time.time() - self.last_time  # calculate the time difference
			self.dt *= FPS_SCALE  # scale the dt by the target framerate for consistency
			self.last_time = time.time()  # reset the last_time with the current time
			self.current_fps = self.clock.get_fps()
			for scene in self.scenes:
				if scene.active:
					scene.update()
					scene.draw()
				if scene.obscured:
					scene.draw()
			self.send_frame()


if __name__ == "__main__":
	game = Game()
	game.scenes = [Launcher(game)]
	game.run()
