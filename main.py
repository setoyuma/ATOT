import pygame as pg
import json
import os

from constants import *
from settings import *
from support import *
from scenes import *

class Game:
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((1000,500), pg.SCALED)
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.display_scroll = pg.math.Vector2()
		self.dt = self.clock.tick(self.FPS) / 1000
		pg.display.set_icon(get_image('./assets/logo.ico'))
		pg.display.set_caption("A Tale Of Time")

		path = "./player_data/players/Setoichi.json"
		if os.path.exists(path):
			with open(path, "r") as f:
				self.loaded_data = json.load(f)
		else:
			self.loaded_data = None

	def draw_fps(self):
		fpsCounter = round(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", (900, 20))

	def run(self):
		while True:
			self.scene.draw()
			self.scene.update()
			self.send_frame()


	def send_frame(self):
		pg.display.flip()
		self.dt = self.clock.tick(self.FPS) / 1000


if __name__ == '__main__':
	game = Game()
	game.scene = Launcher(game)
	game.run()
