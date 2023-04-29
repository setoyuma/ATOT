import pygame as pg
from pygame.locals import *
import sys
import json
import os

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
		
	def character_list(self):
		self.game.screen.blit(self.character_list_img, (700, 100))
		
		if os.listdir('./player_data/players/'):
			player_file = os.listdir('./player_data/players')
			with open(f"./player_data/players/{str(player_file[0])}", 'r') as file:
				player_data = json.load(file)

			player_img = get_image(f'./assets/races/8bit/{str(player_data["race"]).capitalize()}/idle/idle.png')
			self.scaled_player_img = pg.transform.scale(player_img, (32,32))
			draw_text(self.game.screen, f"{player_data['race']} | XP:{player_data['stats']['xp']}", (884,166), size=18, color="white")
		
			self.game.screen.blit(self.scaled_player_img, (745, 150))
		
		else:
			print('no characters')

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
		class_stats = classes["frostknight"]
		
		with open('./player_data/players/Setoichi.json', 'w') as file:
			player_data =  {
				"username": "Setoichi",
				"race": race,
				"class": "frostknight",
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
			json.dump(player_data, file, indent=4)
			file.close()

		self.game.scene = ClassSelect(self.game)
		

class ClassSelect(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.logo = get_image("./assets/UI/abberoth.png")
		character_card = get_image('./assets/UI/character_card.png')
		self.scaled_char_card = pg.transform.scale(character_card, (216, 264))
		
		img = 'assets/UI/buttons/button_plate1.png'
		self.buttons = [
			Button(game, "BACK", (925, 455), self.back, img, img),
			Button(game, "Paladin", (116, 280), self.create_player, img, img, id="paladin"),
			Button(game, "Monk", (372, 280), self.create_player, img, img, id="monk"),
			# Button(game, "Lightbringer", (630, 280), self.create_player, img, img, id="Lightbringer"),
			# Button(game, "Technoki", (892, 280), self.create_player, img, img, id="Technoki")
			]

	def back(self):
		self.game.scene = CharacterSelect(self.game)

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

		for i, icon in enumerate(class_icons.values()):
			scaled_icon = pg.transform.scale(get_image(icon), (64,64))
			self.game.screen.blit(self.scaled_char_card, (5+(257*(i)), 100))
			self.game.screen.blit(scaled_icon, (84+(257*(i)), 148))

		for button in self.buttons:
			button.draw()

		self.game.draw_fps()

	def create_player(self, player_class):
		class_stats = classes[player_class]
		
		with open('./player_data/players/Setoichi.json', 'r') as file:
			old_data = json.load(file)
			file.close()

		with open('./player_data/players/Setoichi.json', 'w') as file:

			player_data =  {
				"username": "Setoichi",
				"race": old_data["race"],
				"class": player_class,
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
			json.dump(player_data, file, indent=4)
			file.close()
		
		self.game.scene = CreateUsername(self.game)

		
class CreateUsername(Scene):
	def __init__(self, game):
		self.game = game
		self.logo = get_image("./assets/UI/abberoth.png")
		self.text_input = TextInput(self.game, 50, (455, 250))

	def back(self):
		self.game.scene = ClassSelect(self.game)

	def update(self):
		self.text_input.update()

		for event in pg.event.get():
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					if self.text_input.input_rect.collidepoint(event.pos):
						self.text_input.active = True
					else:
						self.text_input.active = False

			elif event.type == pg.KEYDOWN:
				# Check for backspace
				if event.key == pg.K_BACKSPACE:
					# get text input from 0 to -1 i.e. end.
					self.text_input.user_text = self.text_input.user_text[:-1]
				elif event.key == pg.K_RETURN:
					self.apply_username(self.text_input.user_text)
				# Unicode standard is used for string
				# formation
				else:
					self.text_input.user_text += event.unicode

			if event.type == pg.QUIT:
				print("Game Closed")
				pg.quit()
				sys.exit()
	
	def apply_username(self, username):
		with open('./player_data/players/Setoichi.json', 'r') as file:
			old_data = json.load(file)
			file.close()

		with open('./player_data/players/Setoichi.json', 'w') as file:

			player_data =  {
				"username": username,
				"race": old_data["race"],
				"class": old_data["class"],
				"rank": old_data["rank"],
				"stats": {
					"xp": old_data["stats"]["xp"],
					"xporb": old_data["stats"]["xporb"],
					"hp": old_data["stats"]["hp"],
					"str": old_data["stats"]["str"],
					"mgck": old_data["stats"]["mgck"],
					"def": old_data["stats"]["def"]
				}
			}
			json.dump(player_data, file, indent=4)
			file.close()
		
		self.game.scene = WorldScene(self.game, player_data)

	def draw(self):
		self.game.screen.blit(self.logo, (0,0))

		draw_text(self.game.screen, "Create Username", (self.game.screen.get_width()/2, 200), color="red", bg_color="black", size=50)

		self.game.draw_fps()


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
		self.game.draw_fps()

	
