import pygame as pg
import sys
from world import World
from world_data import worlds
from settings import *
from pygame.locals import *
from projectile import Projectile, Bullet
from support import *
class Game:

	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.SCALED)
		pg.display.set_caption("Song Of Valks")
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.dt = self.clock.tick(self.FPS) / 1000
		self.running = True
		self.world = World(worlds[1], self.screen)
		self.player = self.world.Player

	def draw_mini_map(self):
		self.mini_map = pg.image.load('./assets/maps/Mini_Map.png')
		scaled_mini_map = pg.transform.scale(self.mini_map, (350,350))
		self.screen.blit(scaled_mini_map, (SCREEN_WIDTH-345, SCREEN_HEIGHT - 750))

		player_stats = self.player.get_player_stats(self.player.player_name)

		draw_text(self.screen, f"STR | {player_stats['str']}", (1185, 210), 20, (255,255,255))
		draw_text(self.screen, f"MGCK | {player_stats['mgck']}", (1185, 240), 20, (255,255,255))
		draw_text(self.screen, f"HP | {player_stats['hp']}", (1075, 210), 20, (255,255,255))
		draw_text(self.screen, f"DEF | {player_stats['def']}", (1075, 240), 20, (255,255,255))
		draw_text(self.screen, f"XP | {player_stats['xp']}", (1080, 270), 20, (255,255,255))
		draw_text(self.screen, f"ORBS | {player_stats['xporb']}", (1175, 270), 20, (255,255,255))
		

		

	def run(self):
		while self.running:
			self.screen.fill("gray")
			
			if self.player.direction.x != 0 or self.player.direction.y != 0:
				pg.key.set_repeat(1,10)
			else:
				pg.key.set_repeat(0)


			for event in pg.event.get():

				if event.type == pg.QUIT:
					print("Game Closed")
					self.running = False
					pg.quit()
					sys.exit()

				if event.type == pg.MOUSEBUTTONDOWN:
					proj = Bullet(self.player.groups[0].offsetPos.x + 60, self.player.groups[0].offsetPos.y + 60)
					self.player.projectiles.append(proj)

					if len(self.player.projectiles) > 4:
						self.player.projectiles.append(proj)

					# proj = Projectile(self.player.groups[0].offsetPos, "red", self.screen)
					# self.player.projectiles.append(proj)

				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						running = False
					# if event.key == K_d:
					# 	self.player.direction.x = 1
					# if event.key == K_a:
					# 	self.player.direction.x = -1
					# if event.key == K_s:
					# 	self.player.direction.y = 1
					# if event.key == K_w:
					# 	self.player.direction.y = -1
					
					if event.key == pg.K_c:
						self.player.create_player()

					
					if event.key == pg.K_x:
						self.player.xp_up(25)
					
					if event.key == pg.K_l:
						self.player.level_up(self.player.player_name, "hp")
						
					
					if event.key == pg.K_f:
						pg.display.toggle_fullscreen()

					if event.key == pg.K_u:
						# self.player.xp_up()
						set = pg.image.load('./assets/gear/Voidknight_Set.png')
						scaled_set = pg.transform.scale(set, (98,98))
						self.player.image = scaled_set
						# self.screen.blit((scaled_set), (self.player.hitbox.center))
						# self.screen.blit(pg.image.load('./assets/gear/Voidknight_Set.png'), (self.player.groups[0].offsetPos.x, self.player.groups[0].offsetPos.y + 98))
			 
					# # Sprinting
					# if event.key == K_LSHIFT:
					# 	print("sprinting")
					# 	self.player.speed = BASE_SPEED + 3

					# Dashing
					if event.key == K_q and self.player.direction.x > 0:
						self.player.rect.x += 20
						self.player.dashing = True
						print("dash")
					if event.key == K_q and self.player.direction.x < 0:
						self.player.rect.x -= 20
						self.player.dashing = True
						print("dash")



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
				proj.update()
				if not self.screen.get_rect().collidepoint(proj.pos):
					self.player.projectiles.remove(proj)

			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=900, y=10)
			self.screen.blit(text,textPos)
			
			self.world.run()
			self.draw_mini_map()
			self.clock.tick(60)
			for proj in self.player.projectiles:
				proj.draw(self.screen)
			pg.display.flip()


if __name__ == '__main__':
	game = Game()
	game.run()
