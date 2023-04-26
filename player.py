import pygame as pg
import json
from settings import *
from support import *
from pallete_swaps import *
from xp_targets import xp_targets
from player_stat_line import StatLine
from pygame.locals import *
from RACES import *
from CLASSES import *

class Player(pg.sprite.Sprite):
	
	def __init__(self, pos, groups, collisionSprites, surface, player_name, player_class, race):
		super().__init__(groups)
		self.collisionSprites = collisionSprites
		self.groups = groups
		# stats
		self.player_name = str(player_name).capitalize()
		self.player_class = str(player_class).capitalize()
		self.race = str(race).capitalize()
		self.xp_targets = xp_targets
		self.hp = 100
		self.mana = 100
		self.projectiles = []

		self.display_surface = surface
		self.spawn_x = pos[0]
		self.spawn_y = pos[1]
		self.image = pg.image.load('./assets/races/Skolfen.png').convert_alpha(self.display_surface)
		scaled_image = pg.transform.scale(self.image, (98,98))
		
		self.image = scaled_image
		# self.rect = self.image.get_rect()
		self.rect = pg.Rect((self.spawn_x, self.spawn_y), (98, 98))
		# self.image = pg.Surface((TILE_SIZE//2, TILE_SIZE))
		# movement
		self.direction = pg.math.Vector2()
		self.speed = BASE_SPEED

		# state vars
		self.running = False
		self.dashing = False
		self.attacking = False
		self.on_left = False
		self.on_right = False

		self.change_rank()

	def switch_image(self):
		if self.direction.x > 0:
			self.image = pg.image.load('./assets/races/Skolfen.png')
			scaled_image = pg.transform.scale(self.image, (98,98))
			self.image = scaled_image
		if self.direction.x < 0:
			self.image = pg.image.load('./assets/races/Skolfen.png')
			scaled_image = pg.transform.scale(self.image, (98,98))
			self.image = scaled_image
		if self.direction.y > 0:
			self.image = pg.image.load('./assets/races/Skolfen.png')
			scaled_image = pg.transform.scale(self.image, (98,98))
			self.image = scaled_image
		if self.direction.y < 0:
			self.image = pg.image.load('./assets/races/Skolfen.png')
			scaled_image = pg.transform.scale(self.image, (98,98))
			self.image = scaled_image

	def horizontalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.x < 0:
					self.rect.left = sprite.rect.right
					self.on_left = True
					self.currentX = self.rect.left
					# print(f'touching left: {self.on_left}')

				if self.direction.x > 0:
					self.rect.right = sprite.rect.left
					self.on_right = True
					self.currentX = self.rect.right
					# print(f'touching right: {self.on_right}')
		# if self.on_left and (self.rect.left < self.currentX or self.direction.x >= 0):
		# 	self.on_left = False
		# if self.on_right and (self.rect.right > self.currentX or self.direction.x <= 0):
		# 	self.on_right = False

	def verticalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.y > 0:
					self.rect.bottom = sprite.rect.top
					self.direction.y = 0
					# self.onGround = True
				if self.direction.y < 0:
					self.rect.top = sprite.rect.bottom
					self.direction.y = 0
					self.onCeiling = True

			# if self.onGround and self.direction.y != 0:
			#     self.onGround = False
		
		# if self.onGround and self.direction.y < 0 or self.direction.y > 1:
		# 	self.onGround = False
		# if self.onCeiling and self.direction.y > 0.1:
		# 	self.onCeiling = False

	def event_handler(self):

		pass

		keys = pg.key.get_pressed()

		if keys[pg.K_d]:
			self.direction.x = 1
		elif keys[pg.K_a]:
			self.direction.x = -1
		else:
			self.direction.x = 0

		if keys[pg.K_w]:
			self.direction.y = -1
		elif keys[pg.K_s]:
			self.direction.y = 1
		else:
			self.direction.y = 0

		# if keys[pg.K_p]:
		# 	self.attacking = True
		# 	print('attack')

		# if keys[pg.K_u]:
		# 	# self.xp_up()
		# 	print("wow")

		# if self.running and keys[pg.K_LSHIFT]:
		# 	self.speed = BASE_SPEED + 3
		# else:
		# 	self.speed = BASE_SPEED

	def get_state(self):
		if self.direction.x != 0:
			self.running = True
		if self.direction.y != 0:
			self.running = True

	def create_player(self):
		
		if self.race in races:
			self.player_race = self.race

		else:
			print(self.race, " Is Not An Available Race")
			print("Not An Available Race")

		match self.player_class:
			case "Monk":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": monk_stats[0],
						"str": monk_stats[1],
						"mgck": monk_stats[2],
						"def": monk_stats[3]
					}
					}
			
			case "Paladin":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": paladin_stats[0],
						"str": paladin_stats[1],
						"mgck": paladin_stats[2],
						"def": paladin_stats[3]
					}
					}
			case "Mistwalker":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": mistwalker_stats[0],
						"str": mistwalker_stats[1],
						"mgck": mistwalker_stats[2],
						"def": mistwalker_stats[3]
					}
					}
			case "Skolbinder":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": skolbinder_stats[0],
						"str": skolbinder_stats[1],
						"mgck": skolbinder_stats[2],
						"def": skolbinder_stats[3]
					}
					}
			case "Ebonguard":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": ebon_guardian_stats[0],
						"str": ebon_guardian_stats[1],
						"mgck": ebon_guardian_stats[2],
						"def": ebon_guardian_stats[3]
					}
					}
			case "Frostknight":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": frost_knight_stats[0],
						"str": frost_knight_stats[1],
						"mgck": frost_knight_stats[2],
						"def": frost_knight_stats[3]
					}
					}
			case "Technomancer":
				new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": 0,
						"xporb": 0,
						"hp": technomancer_stats[0],
						"str": technomancer_stats[1],
						"mgck": technomancer_stats[2],
						"def": technomancer_stats[3]
					}
					}

			case _:
				print("Not An Available Class")
				pass

		with open(f"./player_data/players/{new_player_data['Username']}.json",'w') as file:
			# convert to json and dump.
			json.dump(new_player_data, file, indent = 4)

	def get_player(self, player_name):
		with open(f"./player_data/players/{player_name}.json") as stats:
			player = json.load(stats)
		# print(player)
		# print(f"```Name: {player['Username']}\nRace: {player['Race']}\nClass: {player['Class']}\nRank: {player['Rank']}\nStats: {player['Stats']}```")
		return player

	def get_player_stats(self, player):
		with open(f"./player_data/players/{player}.json") as file:
			player = json.load(file)
		player_stats = player["Stats"]
		# print(player_stats)
		# print(f"{player['Username']}'s stats: ```{str(player_stats)}```")
		return player_stats

	def level_up(self, stat):
		level_increase = 1

		with open(f"./player_data/players/{self.player_name}.json", "r") as file:
			player = json.load(file)

			player_stats = player["Stats"]
			
			if int(player_stats["xporb"]) > 0: 
				match stat:
					case "hp":
						player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": player["Rank"],
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"] - 1,
								"hp": int(player_stats["hp"]) + level_increase,
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
						with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)

					case "str":
						player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": player["Rank"],
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"] - 1,
								"hp": player_stats["hp"],
								"str": player_stats["str"] + level_increase,
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
						with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)

					case "mgck":
						player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": player["Rank"],
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"] - 1,
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"] + level_increase,
								"def": player_stats["def"]
							}
							}
						with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)

					case "def":
						player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": player["Rank"],
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"] - 1,
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"] + level_increase
							}
							}
						with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)

					case _:
						print("Not An Available Stat")
						pass
			else:
				print("Not Enough XP Orbs To Level Up")

	def xp_up(self, xp_amount):
		player_stats = self.get_player_stats(self.player_name)

		if xp_amount >= 25:
			new_player_data =  {
					"Username": self.player_name,
					"Race": self.race,
					"Class": self.player_class,
					"Rank": "Civilian",
					"Stats": {
						"xp": player_stats["xp"] + xp_amount,
						"xporb": self.get_player(self.player_name)["Stats"]["xporb"] + 1,
						"hp": self.get_player(self.player_name)["Stats"]["hp"],
						"str": self.get_player(self.player_name)["Stats"]["str"],
						"mgck": self.get_player(self.player_name)["Stats"]["mgck"],
						"def": self.get_player(self.player_name)["Stats"]["def"],
					}
					}

		else:
			new_player_data =  {
						"Username": self.player_name,
						"Race": self.race,
						"Class": self.player_class,
						"Rank": "Civilian",
						"Stats": {
							"xp": player_stats["xp"] + xp_amount,
							"xporb": self.get_player(self.player_name)["Stats"]["xporb"],
							"hp": self.get_player(self.player_name)["Stats"]["hp"],
							"str": self.get_player(self.player_name)["Stats"]["str"],
							"mgck": self.get_player(self.player_name)["Stats"]["mgck"],
							"def": self.get_player(self.player_name)["Stats"]["def"],
						}
						}

		with open(f"./player_data/players/{self.player_name}.json", "w") as file:
			json.dump(new_player_data, file, indent=4)
			file.close()
	
	def change_rank(self):
		with open(f"./player_data/players/{self.player_name}.json", "r") as file:
			player = json.load(file)
			player_stats = player["Stats"]
		
		if player["Stats"]["xp"] >= xp_targets["Civilian"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Page",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Page"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Squire",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Squire"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Knight",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Knight"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Mage",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Mage"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Oracle",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Oracle"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Spellweaver",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Spellweaver"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Lord",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Lord"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Voidtouched",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
		if player["Stats"]["xp"] >= xp_targets["Voidtouched"]:
			player_data =  {
							"Username": player["Username"],
							"Race": player["Race"],
							"Class": player["Class"],
							"Rank": "Shaper",
							"Stats": {
								"xp": player_stats["xp"],
								"xporb": player_stats["xporb"],
								"hp": player_stats["hp"],
								"str": player_stats["str"],
								"mgck": player_stats["mgck"],
								"def": player_stats["def"]
							}
							}
			with open(f"./player_data/players/{self.player_name}.json", "w") as file:
							json.dump(player_data, file, indent = 4)
							file.close()
		
	#broken
	def write_json(self, new_data, player_name):
		
		with open(f"./player_data/players/{new_player_data['username']}.json",'r+') as file:
			# First we load existing data into a dict.
			player_data = json.load(file)
			# Join new_data with file_data inside emp_details
			player_data["player"].append(new_data)
			# Sets file's current position at offset.
			file.seek(0)
			# convert back to json.
			json.dump(player_data, file, indent = 4)

	def update(self):
		self.switch_image()
		self.event_handler()
		self.rect.x += self.direction.x * self.speed
		self.horizontalCollisions()
		self.rect.y += self.direction.y * self.speed
		self.verticalCollisions()
		self.get_state()
		self.hitbox = pg.Rect((self.groups[0].offsetPos.x + 20, self.groups[0].offsetPos.y), (60,98))

		self.change_rank()
		
		# self.image = blue_ebonheart(self.image)  # pallet swapped ebonheart