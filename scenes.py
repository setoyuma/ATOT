import pygame as pg
from pygame.locals import *
import sys
import json
import os

from button import Button
from world import World
from projectile import *
from constants import *
from settings import *
from support import *

class Scene:
	def __init__(self, game, initial_bg=None):
		self.game = game
		self.active = True
		self.obscured = False

	def update(self):
		pass

	def draw(self):
		pass

	def check_universal_events(self, pressed_keys, event):
		quit_attempt = False
		if event.type == pygame.QUIT:
			quit_attempt = True
		elif event.type == pygame.KEYDOWN:
			alt_pressed = pressed_keys[pygame.K_LALT] or \
				pressed_keys[pygame.K_RALT]
			if event.key == pygame.K_F4 and alt_pressed:
				quit_attempt = True
		if quit_attempt:
			pygame.quit()
			sys.exit()

class Launcher(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.logo = get_image("./assets/UI/abberoth.png")
		self.character_list_img = get_image('./assets/UI/character_list.png')
		#self.scaled_player_img = pg.transform.scale(self.game.player.image, (32,32))

		img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(game, "NEW", (925, 355), None, img, img),
			Button(game, "PLAY", (925, 455), self.load_world, img, img)
			#Button(game, "QUIT", (self.game.settings["screen_width"] - 100, 50,), pg.quit, img, img)
		]
		
	def patch_notes(self):
		patch_notes_surf = pg.Surface((240,250))
		patch_notes_surf.fill("white")
		self.game.screen.blit(patch_notes_surf, (10,125))
		patch_notes_rect = patch_notes_surf.get_rect(topleft=(10,175))
		# pg.draw.rect(self.screen, "red", patch_notes_rect)
		draw_text(self.game.screen, "Patch Notes", (120,150), color="black")
		text_line_wrap(self.game.screen, f"{notes['Launcher']}"+f"{notes['Game']}", "black", patch_notes_rect, pg.font.Font(None, 30))

	def load_world(self):
		self.game.scene = WorldScene(self.game, self.game.loaded_data)

	def update(self):
		for event in pg.event.get():
			for button in self.buttons:
				button.update(event)

			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()

	def draw(self):
		self.game.screen.fill("black")
		self.game.screen.blit(self.logo, (0,0))
		# self.character_list()
		self.patch_notes()

		for button in self.buttons:
			button.draw()

		self.game.draw_fps()

class WorldScene(Scene):
	def __init__(self, game, player_data):
		super().__init__(game)
		self.game.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.SCALED)
		self.game.world = World(self.game, worlds[1], self.game.screen)
		self.game.player = self.game.world.player

		mini_map = get_image('./assets/UI/maps/Mini_Map.png')
		self.scaled_mini_map = pg.transform.scale(mini_map, (350,350))

	def update(self):
		if self.game.player.direction.x != 0 or self.game.player.direction.y != 0:
			pg.key.set_repeat(1,10)
		else:
			pg.key.set_repeat(0)

		mouseX, mouseY = pg.mouse.get_pos()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()

			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
						self.game.world.player.projectiles.append(Projectile(self.game.world.player.x, self.game.world.player.y, mouseX, mouseY))
				
				# if event.button in projectile_types.keys():
				# 	self.game.player.casting_projectile = True
				# 	self.game.player.projectile_type = projectile_types[event.button]
					# proj = RadialBullet(*self.player.groups[0].offsetPos, 5)
			elif event.type == pg.MOUSEBUTTONUP:
				self.game.player.casting_projectile = False

			elif event.type == KEYDOWN:
				if event.key == pg.K_f:
					pg.display.toggle_fullscreen()

			elif event.type == KEYUP:
				if event.key == K_a or event.key == K_d:
					self.game.player.direction.x = 0
				elif event.key == K_w or event.key == K_s:
					self.game.player.direction.y = 0

	def draw(self):
		self.game.screen.fill("black")
		self.game.world.main(self.game.screen)
		self.game.draw_fps()

	