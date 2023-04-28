import pygame as pg
from pygame.locals import *
import json
import sys

from button import Button
from world import World
from projectile import *
from CONSTANTS import *
from settings import *
from support import *

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
		self.world = World(worlds[1], self.screen, self)
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
					if event.button == 1:
						# proj = RadialBullet(*self.player.groups[0].offsetPos, 5)
						proj = Bullet(self.player.groups[0].offsetPos.x + 35, self.player.groups[0].offsetPos.y + 40)
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
				if not self.screen.get_rect().collidepoint((proj.pos[0], proj.pos[1])):
					self.player.projectiles.remove(proj)

			
			self.world.run()
			self.draw_mini_map()
			self.clock.tick(60)
			for proj in self.player.projectiles:
				proj.draw(self.screen)
			
			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=900, y=10)
			self.screen.blit(text,textPos)
			pg.display.flip()

class Launcher():

	def __init__(self, game):
		pg.init()
		self.game = game
		self.screen = pg.display.set_mode((1000,500), pg.SCALED)
		pg.display.set_caption("A Tale Of Time")
		self.game_icon = pg.image.load('./assets/logo.ico')
		pg.display.set_icon(self.game_icon)
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.dt = self.clock.tick(self.FPS) / 1000
		self.running = True
	
	def character_list(self):
		character_list_img = pg.image.load('./assets/UI/character_list.png')

		scaled_char_list_img = pg.transform.scale(character_list_img, (580,320))
		
		self.screen.blit(character_list_img, (700, 100))
		# self.screen.blit(scaled_char_list_img, (720, 100))

		draw_text(self.screen, f"{self.game.player.get_player(self.game.player.player_name)['Race']} | XP:{self.game.player.get_player(self.game.player.player_name)['Stats']['xp']}", (884,166), size=18, color="white")

		self.scaled_player_img = pg.transform.scale(self.game.player.image, (32,32))
		self.screen.blit(self.scaled_player_img, (745, 150))

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
		self.cs = Character_select(self.game)
		button_img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(self, "PLAY", (925, 455), self.run_game, button_img, button_img, text_size=30),
			Button(self, "NEW", (925, 355), self.cs.run, button_img, button_img, text_size=30),
			# Button(self.game, "QUIT", (self.game.settings["screen_width"] - 100, 50,), pg.quit, "assets/ui/buttons/button_plate1.png", "assets/ui/buttons/button_plate1.png", text_size=30)
		]
		input_handler = Input_Handler(self, 30, (500,500))

		while self.running:
			self.screen.fill("black")
			self.logo = get_image("./assets/UI/abberoth.png")
			self.screen.blit(self.logo, (0,0))
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
					if input_handler.input_rect.collidepoint(event.pos):
						input_handler.active = True
					else:
						input_handler.active = False
					

				if event.type == pg.KEYDOWN:
					# Check for backspace
					if event.key == pg.K_BACKSPACE:
						# get text input from 0 to -1 i.e. end.
						input_handler.user_text = input_handler.user_text[:-1]
					# Unicode standard is used for string
					# formation
					else:
						input_handler.user_text += event.unicode

						
			for button in self.buttons:
				button.draw()

			# input_handler.update()

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
		
		self.game = game
		self.screen = pg.display.set_mode((1000,500), pg.SCALED)
		pg.display.set_caption("A Tale Of Time")
		self.clock = pg.time.Clock()
		self.FPS = 60
		self.dt = self.clock.tick(self.FPS) / 1000
		self.running = True

	def draw(self):
		self.logo = get_image("./assets/UI/abberoth.png")
		self.screen.blit(self.logo, (0,0))
		self.character_card =get_image('./assets/UI/character_card.png')
		scaled_char_card = pg.transform.scale(self.character_card, (216, 264))

		ebonheart = get_image('./assets/races/8bit/Ebonheart/idle/idle.png')
		voidkin = get_image('./assets/races/8bit/Voidkin/idle/idle.png')
		lightbringer = get_image('./assets/races/8bit/Lightbringer/idle/idle.png')
		technoki = get_image('./assets/races/8bit/Technoki/idle/idle.png')

		scaled_ebonheart = pg.transform.scale(ebonheart,(64,64))
		scaled_voidkin = pg.transform.scale(voidkin,(64,64))
		scaled_lightbringer = pg.transform.scale(lightbringer,(64,64))
		scaled_technoki = pg.transform.scale(technoki,(64,64))


		class_imgs = [
			scaled_ebonheart,
			scaled_voidkin,
			scaled_lightbringer,
			scaled_technoki
		]

		

		for i in range(len(class_imgs)):
			
			self.screen.blit(scaled_char_card, (5+(258*(i)), 100))
			self.screen.blit(class_imgs[i], (84+(258*(i)), 148))

	def update(self):
		launcher = Launcher(self.game)
		
		while True:
			self.draw()
			
			button_img = 'assets/UI/buttons/button_plate1.png'
			self.buttons = [
				Button(self, "BACK", (925, 455), launcher.launch, button_img, button_img, text_size=30),
				Button(self, "Ebonheart", (116, 280), self.game.player.create_player("Ebonheart"), button_img, button_img, text_size=30),
				Button(self, "Voidkin", (372, 280), self.game.player.create_player("Voidkin"), button_img, button_img, text_size=30),
				Button(self, "Lightbringer", (630, 280), self.game.player.create_player("Lightbringer"), button_img, button_img, text_size=30),
				Button(self, "Technoki", (892, 280), self.game.player.create_player("Technoki"), button_img, button_img, text_size=30)
			]

			for event in pg.event.get():
				
				for button in self.buttons:
					button.update(event)

				if event.type == pg.QUIT:
					print("Game Closed")
					self.running = False
					pg.quit()
					sys.exit()

			for button in self.buttons:
				button.draw()

			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=900, y=10)
			self.screen.blit(text,textPos)

			self.clock.tick(60)
			pg.display.flip()

	def run(self):
		self.update()


if __name__ == '__main__':
	launcher = Launcher(Game())
	launcher.launch()
