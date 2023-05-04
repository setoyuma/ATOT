import pygame as pg
from support import *
from constants import *
from tile import *
from player import Player
from enemy import Enemy
from player_stat_line import StatLine

class World:

	def __init__(self, game, world_data, display):
		self.game = game
		self.world_data = world_data
		self.display_surface = display
		self.enemies = [
			Enemy(self.game, 600, 600, 64, 64),
			]
		self.ground = get_image('./assets/world/Abberoth.png')

		# groups
		self.terrainSprites = pg.sprite.Group()
		self.playerSprites = pg.sprite.Group()
		self.collisionSprites = pg.sprite.Group() # sprites with collision

		# layouts 
		# player
		player_layout = import_csv_layout(world_data['player'])
		self.player = pg.sprite.GroupSingle()
		self.player_setup(player_layout)

		# terrain layout
		terrain_layout = import_csv_layout(world_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

	def create_tile_group(self, layout, type):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
					
					if type == 'terrain':
						terrain_tile_list = import_cut_graphics(
							'./assets/world/tiles/tileset.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(TILE_SIZE, x, y, tile_surface, [self.terrainSprites, self.collisionSprites])
						self.terrainSprites.add(sprite)
						self.terrainSprites.draw(self.display_surface)
					
	def player_setup(self, layout):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				
				if val == '0':
					self.player = Player(self.game, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 64, 64, self.playerSprites, self.collisionSprites)
					self.playerSprites.add(self.player)
	def player_handler(self):
		self.player.main(self.display_surface)
		
	def draw_shadows(self):
		# player shadow
		self.display_surface.blit(pg.transform.scale(get_image("./assets/player/shadow.png"), (64,28)), (self.player.rect.centerx-32, self.player.rect.centery+16))

		# enemy shadow
		for enemy in self.enemies:
			self.display_surface.blit(pg.transform.scale(get_image("./assets/player/shadow.png"), (64,28)), (enemy.rect.centerx-32, enemy.rect.centery+16))

	def draw_ground(self):
		self.display_surface.blit(self.ground, (0-self.game.display_scroll.x,0-self.game.display_scroll.y))

	def draw_terrain(self):
		# for sprite in self.terrainSprites.sprites():
		# 	sprite.x - self.game.display_scroll.x
		# 	sprite.y - self.game.display_scroll.y

		self.terrainSprites.draw(self.display_surface)

	def projectile_handler(self):
		for proj in self.player.projectiles:
			proj.main(self.display_surface)

	def enemy_handler(self):
		for enemy in self.enemies:
			enemy.main(self.display_surface, self.player)

	def layer_sort(self):
		self.draw_ground()
		self.draw_terrain()
		self.draw_shadows()
		self.playerSprites.draw(self.display_surface)
		self.collisionSprites.update()

	def main(self, display):
		self.layer_sort()
		self.player_handler()
		self.projectile_handler()
		self.enemy_handler()
		
		statline = StatLine("text", 64, self.player, (self.player.rect.x + 50, self.player.rect.y-30), "green", self.display_surface)

		statline.update()