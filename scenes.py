import pygame as pg
from pygame.locals import *
import sys

from button import Button
from world import World
from projectile import *
from CONSTANTS import *
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
		self.scaled_char_list_img = pg.transform.scale(self.character_list_img, (580,320))

		img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(game, "NEW", (925, 355), self.load_cs, img, img)
			#Button(game, "QUIT", (self.game.settings["screen_width"] - 100, 50,), pg.quit, img, img)
		]
		if self.game.loaded_data is not None:
			self.buttons.append(Button(game, "PLAY", (925, 455), self.load_world, img, img))
		
		self.input_handler = Input_Handler(self, 30, (500,500))

	def character_list(self):
		self.game.screen.blit(self.character_list_img, (700, 100))
		#draw_text(self.game.screen, f"{self.game.player.player_data['race']} | XP:{self.game.player.player_data['stats']['xp']}", (884,166), size=18, color="white")
		#self.game.screen.blit(self.scaled_player_img, (745, 150))

	def patch_notes(self):
		patch_notes_surf = pg.Surface((240,250))
		patch_notes_surf.fill("white")
		self.game.screen.blit(patch_notes_surf, (10,125))
		patch_notes_rect = patch_notes_surf.get_rect(topleft=(10,175))
		# pg.draw.rect(self.screen, "red", patch_notes_rect)
		draw_text(self.game.screen, "Patch Notes", (120,150), color="black")
		text_line_wrap(self.game.screen, f"{notes['Launcher']}"+f"{notes['Game']}", "black", patch_notes_rect, pg.font.Font(None, 30))

	def load_cs(self):
		self.game.scene = CharacterSelect(self.game)

	def load_world(self):
		self.game.scene = WorldScene(self.game, self.game.loaded_data)

	def update(self):
		# input_handler.update()

		for event in pg.event.get():
			for button in self.buttons:
				button.update(event)

			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()

			elif event.type == pg.MOUSEBUTTONDOWN:
				if self.input_handler.input_rect.collidepoint(event.pos):
					self.input_handler.active = True
				else:
					self.input_handler.active = False

			elif event.type == pg.KEYDOWN:
				# Check for backspace
				if event.key == pg.K_BACKSPACE:
					# get text input from 0 to -1 i.e. end.
					self.input_handler.user_text = self.input_handler.user_text[:-1]
				# Unicode standard is used for string
				# formation
				else:
					self.input_handler.user_text += event.unicode

	def draw(self):
		self.game.screen.fill("black")
		self.game.screen.blit(self.logo, (0,0))
		self.character_list()
		self.patch_notes()

		for button in self.buttons:
			button.draw()

		self.game.draw_fps()


class CharacterSelect(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.logo = get_image("./assets/UI/abberoth.png")
		character_card = get_image('./assets/UI/character_card.png')
		self.scaled_char_card = pg.transform.scale(character_card, (216, 264))

		ebonheart = get_image('./assets/races/8bit/Ebonheart/idle/idle.png')
		voidkin = get_image('./assets/races/8bit/Voidkin/idle/idle.png')
		lightbringer = get_image('./assets/races/8bit/Lightbringer/idle/idle.png')
		technoki = get_image('./assets/races/8bit/Technoki/idle/idle.png')

		scaled_ebonheart = pg.transform.scale(ebonheart,(64,64))
		scaled_voidkin = pg.transform.scale(voidkin,(64,64))
		scaled_lightbringer = pg.transform.scale(lightbringer,(64,64))
		scaled_technoki = pg.transform.scale(technoki,(64,64))

		self.class_imgs = [
			scaled_ebonheart,
			scaled_voidkin,
			scaled_lightbringer,
			scaled_technoki
		]

		img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(game, "BACK", (925, 455), self.back, img, img),
			Button(game, "Ebonheart", (116, 280), self.create_player, img, img, id="Ebonheart"),
			Button(game, "Voidkin", (372, 280), self.create_player, img, img, id="Voidkin"),
			Button(game, "Lightbringer", (630, 280), self.create_player, img, img, id="Lightbringer"),
			Button(game, "Technoki", (892, 280), self.create_player, img, img, id="Technoki")
		]

	def update(self):
		for event in pg.event.get():
			for button in self.buttons:
				button.update(event)

			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()

	def draw(self):
		self.game.screen.blit(self.logo, (0,0))

		for i, image in enumerate(self.class_imgs):
			self.game.screen.blit(self.scaled_char_card, (5+(258*(i)), 100))
			self.game.screen.blit(image, (84+(258*(i)), 148))

		for button in self.buttons:
			button.draw()

		self.game.draw_fps()

	def back(self):
		self.game.scene = Launcher(self.game)

	def create_player(self, race):
		class_stats = classes["Frostknight"]
		player_data =  {
			"username": "Setoichi",
			"race": race,
			"class": "Frostknight",
			"rank": "civilian",
			"stats": {
				"xp": 0,
				"xporb": 0,
				"hp": class_stats[0],
				"str": class_stats[1],
				"mgck": class_stats[2],
				"def": class_stats[3]
			}
		}
		self.game.scene = WorldScene(self.game, player_data)


class WorldScene(Scene):
	def __init__(self, game, player_data):
		super().__init__(game)
		self.game.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pg.SCALED)
		self.game.world = World(worlds[1], player_data, self.game.screen, self.game)
		self.game.player = self.game.world.Player

		mini_map = get_image('./assets/maps/Mini_Map.png')
		self.scaled_mini_map = pg.transform.scale(mini_map, (350,350))

	def update(self):
		if self.game.player.direction.x != 0 or self.game.player.direction.y != 0:
			pg.key.set_repeat(1,10)
		else:
			pg.key.set_repeat(0)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()

			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button in projectile_types.keys():
					self.game.player.casting_projectile = True
					self.game.player.projectile_type = projectile_types[event.button]
					# proj = RadialBullet(*self.player.groups[0].offsetPos, 5)
			elif event.type == pg.MOUSEBUTTONUP:
				self.game.player.casting_projectile = False

			elif event.type == KEYDOWN:
				if event.key == pg.K_c:
					self.game.player.create_player()
				elif event.key == pg.K_x:
					self.game.player.xp_up(25)
				elif event.key == pg.K_l:
					self.game.player.level_up("hp")
				elif event.key == pg.K_f:
					pg.display.toggle_fullscreen()

			elif event.type == KEYUP:
				if event.key == K_a or event.key == K_d:
					self.game.player.direction.x = 0
				elif event.key == K_w or event.key == K_s:
					self.game.player.direction.y = 0

	def draw(self):
		self.game.screen.fill("black")
		self.game.world.run()
		self.draw_mini_map()
		self.game.draw_fps()

	def draw_mini_map(self):
		self.game.screen.blit(self.scaled_mini_map, (SCREEN_WIDTH-345, SCREEN_HEIGHT - 750))
		player_stats = self.game.player.stats
		draw_text(self.game.screen, f"STR | {player_stats['str']}", (1185, 210), 20, (255,255,255))
		draw_text(self.game.screen, f"MGCK | {player_stats['mgck']}", (1185, 240), 20, (255,255,255))
		draw_text(self.game.screen, f"HP | {player_stats['hp']}", (1075, 210), 20, (255,255,255))
		draw_text(self.game.screen, f"DEF | {player_stats['def']}", (1075, 240), 20, (255,255,255))
		draw_text(self.game.screen, f"XP | {player_stats['xp']}", (1080, 270), 20, (255,255,255))
		draw_text(self.game.screen, f"ORBS | {player_stats['xporb']}", (1175, 270), 20, (255,255,255))
