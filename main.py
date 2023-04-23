import pygame as pg
import sys
from world import World
from world_data import worlds
from settings import *
from pygame.locals import *
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
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						running = False
					if event.key == K_d:
						self.world.Player.direction.x = 1
					if event.key == K_a:
						self.world.Player.direction.x = -1
					if event.key == K_s:
						self.world.Player.direction.y = 1
					if event.key == K_w:
						self.world.Player.direction.y = -1
			 
					# Sprinting
					if event.key == K_LSHIFT:
						print("sprinting")
						self.world.Player.speed = BASE_SPEED + 3

					# Dashing
					if event.key == K_q and self.world.Player.direction.x > 0:
						self.world.Player.rect.x += 120
						print("dash")
					if event.key == K_q and self.world.Player.direction.x < 0:
						self.world.Player.rect.x -= 120
						print("dash")



				if event.type == KEYUP:
					if event.key == K_a or event.key == K_d:
						self.world.Player.direction.x = 0
					if event.key == K_w or event.key == K_s:
						self.world.Player.direction.y = 0

					# Sprinting
					if event.key == K_LSHIFT:
						self.world.Player.speed = BASE_SPEED

					# Dashing
					if event.key == K_q and self.world.Player.direction.x > 0:
						self.world.Player.rect.x -= 0
						pass
			self.world.run()
			self.clock.tick(60)
			pg.display.flip()


if __name__ == '__main__':
	game = Game()
	game.run()
