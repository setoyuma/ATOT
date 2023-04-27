import pygame as pg

from player import Player
from camera import CameraGroup
from support import *
from settings import *
from tile import *
from ui import UI
from player_stat_line import StatLine
class World:
	def __init__(self, world_data, surface, game):
		self.display_surface = surface
		self.game = game

		# UI
		self.ui = UI(self.display_surface)

		# sprite group setup
		self.visibleSprites = CameraGroup()  # sprites here will be drawn
		# self.visibleSprites = pg.sprite.Group()   # sprites here will be drawn
		self.activeSprites = pg.sprite.Group()  # sprites in here will be updated
		# sprites that the player can collide with
		self.collisionSprites = pg.sprite.Group()

		# projectile sprites
		self.projectileSprites = pg.sprite.Group()

		# ground layout
		ground_layout = import_csv_layout(world_data['ground'])
		self.ground_sprites = self.create_tile_group(
			ground_layout, 'ground')
		
		# terrain layout
		terrain_layout = import_csv_layout(world_data['terrain'])
		self.terrain_sprites = self.create_tile_group(
			terrain_layout, 'terrain')
		
		# decoration layout
		deco_layout = import_csv_layout(world_data['deco'])
		self.deco_sprites = self.create_decoration_group(
			deco_layout, 'deco')

		# player
		player_layout = import_csv_layout(world_data['player'])
		self.player = pg.sprite.GroupSingle()
		self.goal = pg.sprite.GroupSingle()
		self.player_setup(player_layout)

	def create_decoration_group(self, layout, type):
		sprite_group = pg.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
	
					if type == 'deco' and val == '0':
						deco_list = get_image(
							'./assets/tiles/deco/trees/tree.png')
						deco_surface = deco_list
						sprite = StaticTile(TILE_SIZE, x, y, deco_surface, [self.visibleSprites])
					
					if type == 'deco' and val == '1':
						deco_list = get_image(
							'./assets/tiles/deco/trees/abborath_tree.png')
						deco_surface = deco_list
						sprite = StaticTile(TILE_SIZE, x, y, deco_surface, [self.visibleSprites])

	def create_tile_group(self, layout, type):
		sprite_group = pg.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE

					if type == 'terrain':
						terrain_tile_list = import_cut_graphics(
							'./assets/tiles/Static_Tile.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(TILE_SIZE, x, y, tile_surface, [self.visibleSprites, self.collisionSprites])
						pg.draw.rect(self.display_surface, "red", sprite.rect)
					
					if type == 'ground':
						ground_tile_list = import_cut_graphics(
							'./assets/tiles/grasstileset.png')
						ground_surface = ground_tile_list[int(val)]
						sprite = StaticTile(TILE_SIZE, x, y, ground_surface, [self.visibleSprites])
						pg.draw.rect(self.display_surface, "red", sprite.rect)
					
					
					
					sprite_group.add(sprite)
		return sprite_group

	def player_setup(self, layout):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					print(f"Proper Spawn x: {x}")
					print(f"Proper Spawn y: {y}")
					print("")
					self.Player = Player(self.game, (x, y), [self.visibleSprites, self.activeSprites], self.collisionSprites, self.display_surface, "setoichi", "Frostknight", "Technoki")
					self.player.add(self.Player)
					self.visibleSprites.add(self.player)
				if val == '1':
					pass

	def run(self):
		self.visibleSprites.customDraw(self.Player)
		self.player.update()
		# pg.draw.rect(self.display_surface, "blue", self.Player.hitbox)

		
		self.stat_line = StatLine("", 25, self.Player, (self.visibleSprites.offsetPos.x + 50, self.visibleSprites.offsetPos.y- 15), "white", self.display_surface)
		self.stat_line.update()
		# self.visibleSprites.update()
		# self.visibleSprites.draw(self.display_surface)
		self.ui.show_health(self.Player.hp, 100)
		self.ui.show_mana(self.Player.mana, 100)
