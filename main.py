import pygame as pg
import sys
import json
from world import World
from world_data import worlds
from settings import *
from pygame.locals import *
from projectile import Bullet
from support import *
from button import Button
class Game:

	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.SCALED)
		pg.display.set_caption("A Tale Of Time")
		self.game_icon = pg.image.load('./assets/logo.ico')
		pg.display.set_icon(self.game_icon)
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

					if event.key == pg.K_c:
						self.player.create_player()

					if event.key == pg.K_x:
						self.player.xp_up(25)
					
					if event.key == pg.K_l:
						self.player.level_up("hp")
						
					if event.key == pg.K_f:
						pg.display.toggle_fullscreen()

				if event.type == KEYUP:
					if event.key == K_a or event.key == K_d:
						self.player.direction.x = 0
					if event.key == K_w or event.key == K_s:
						self.player.direction.y = 0

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

class Launcher(Game):

	def __init__(self):
		pg.init()
		super().__init__()
		self.screen = pg.display.set_mode((1000,500), pg.SCALED)
		pg.display.set_caption("A Tale Of Time")
		self.game_icon = pg.image.load('./assets/logo.ico')
		pg.display.set_icon(self.game_icon)
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.dt = self.clock.tick(self.FPS) / 1000
		self.running = True
		self.cs = Character_select(self)
	
	def character_list(self):
		draw_text(self.screen, "Characters", (915,125), bg_color="white", color="black")
		draw_text(self.screen, f"{self.player.get_player(self.player.player_name)['Race']} | XP:{self.player.get_player(self.player.player_name)['Stats']['xp']}", (900,150), color="black", bg_color="white")

	def patch_notes(self):
		# notes
		with open('./temp/0-0-1.json', 'r') as file:
			notes = json.load(file)
		patch_notes_surf = pg.Surface((240,250))
		patch_notes_surf.fill("white")
		self.screen.blit(patch_notes_surf, (10,125))
		patch_notes_rect = patch_notes_surf.get_rect(topleft=(10,175))
		# pg.draw.rect(self.screen, "red", patch_notes_rect)
		draw_text(self.screen, "Patch Notes", (120,150), color="black")
		text_line_wrap(self.screen, f"{notes['Launcher']}"+f"{notes['Game']}", "black", patch_notes_rect, pg.font.Font(None, 30))


	def run_game(self):
		self.game = Game()
		self.game.run()

	def launch(self):
		button_img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(self, "PLAY", (925, 455), self.run_game, button_img, button_img, text_size=30),
			Button(self, "NEW", (925, 355), self.cs.run, button_img, button_img, text_size=30),
			# Button(self.game, "QUIT", (self.game.settings["screen_width"] - 100, 50,), pg.quit, "assets/ui/buttons/button_plate1.png", "assets/ui/buttons/button_plate1.png", text_size=30)
		]
		while self.running:
			self.screen.fill("black")
			self.logo = pg.image.load("./assets/logo.png")
			scaled_logo = pg.transform.scale(self.logo, (64,64))
			self.screen.blit(self.logo, (250, 25))
			self.character_list()
			self.patch_notes()

			for event in pg.event.get():
				
				for button in self.buttons:
					button.update(event)

				if event.type == pg.QUIT:
					print("Game Closed")
					self.running = False
					pg.quit()
					sys.exit()

				if event.type == pg.MOUSEBUTTONDOWN:
					pass

				if event.type == KEYDOWN:
					pass

				if event.type == KEYUP:
					pass

			for button in self.buttons:
				button.draw()

			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=900, y=10)
			self.screen.blit(text,textPos)
			
			self.clock.tick(60)
			pg.display.flip()

class Character_select():
	def __init__(self, game):
		pg.init()
		# super().__init__()
		self.game = game
		self.screen = pg.display.set_mode((1000,500), pg.SCALED)
		pg.display.set_caption("A Tale Of Time")
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.dt = self.clock.tick(self.FPS) / 1000
		self.running = True

	def draw(self):
		self.character_select = pg.image.load('./assets/race_select.png')
		scaled_cs = pg.transform.scale(self.character_select, (1000,500))
		self.screen.blit(scaled_cs, (0,0))

	def update(self):
		font = pg.font.Font(None,30)
		fpsCounter = str(int(self.clock.get_fps()))
		text = font.render(f"FPS: {fpsCounter}",True,'white','black')
		textPos = text.get_rect(centerx=900, y=10)
		self.screen.blit(text,textPos)
		
		self.clock.tick(60)
		pg.display.flip()

	def run(self):
		self.draw()
		self.update()


if __name__ == '__main__':
	launcher = Launcher()
	launcher.launch()
