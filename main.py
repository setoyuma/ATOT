import pygame as pg
import sys
from world import World
from world_data import worlds
from settings import *
from pygame.locals import *
from projectile import Projectile
class Game:

	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pg.display.set_caption("Song Of Valks")
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.running = True
		self.world = World(worlds[1], self.screen)
		self.player = self.world.Player


	def run(self):
		while self.running:
			self.screen.fill("gray")
			
			if self.player.direction.x != 0 or self.player.direction.y != 0:
				pg.key.set_repeat(1,10)


			for event in pg.event.get():

				if event.type == pg.QUIT:
					print("Game Closed")
					self.running = False
					pg.quit()
					sys.exit()

				if event.type == pg.MOUSEBUTTONDOWN:
					proj = Projectile(self.player.groups[0].offsetPos, "red", self.screen)
					self.player.projectiles.append(proj)
					print("shoot")

				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						running = False
					if event.key == K_d:
						self.player.direction.x = 1
					if event.key == K_a:
						self.player.direction.x = -1
					if event.key == K_s:
						self.player.direction.y = 1
					if event.key == K_w:
						self.player.direction.y = -1

					if event.key == pg.K_u:
						self.player.xp_up()
			 
					# # Sprinting
					# if event.key == K_LSHIFT:
					# 	print("sprinting")
					# 	self.player.speed = BASE_SPEED + 3

					# # Dashing
					# if event.key == K_q and self.player.direction.x > 0:
					# 	self.player.rect.x += 200
					# 	self.player.dashing = True
					# 	print("dash")
					# if event.key == K_q and self.player.direction.x < 0:
					# 	self.player.rect.x -= 200
					# 	self.player.dashing = True
					# 	print("dash")



				if event.type == KEYUP:
					if event.key == K_a or event.key == K_d:
						self.player.direction.x = 0
					if event.key == K_w or event.key == K_s:
						self.player.direction.y = 0

					# # Sprinting
					# if event.key == K_LSHIFT:
					# 	self.player.speed = BASE_SPEED

					# Dashing
					if event.key == K_q and self.player.direction.x > 0:
						self.player.rect.x -= 0
						self.player.dashing = False
						pass

			for proj in self.player.projectiles:
				proj.draw()
				proj.move()
				proj.update()

			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=1000, y=10)
			self.screen.blit(text,textPos)

			self.world.run()
			self.clock.tick(60)
			pg.display.flip()
			self.player.check_stats(self.player.get_stat_sheet())


if __name__ == '__main__':
	game = Game()
	game.run()
