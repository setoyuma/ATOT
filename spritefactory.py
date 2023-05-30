import pygame as pg

from tile import *
from support import *
from cCONSTANTSonstants import *
from enemy import Enemy
from player import Player

class SpriteFactory:
	def __init__(self, game, collisionSprites):
		self.game = game
		self.collisionSprites = collisionSprites

	def create_sprite(self, sprite_type, x, y, width, height, val=0):
		match sprite_type:
			case 'player':
				return Player(self.game, x, y, width, height, self.collisionSprites)
			case 'enemy':
				return Enemy(self.game, x, y, width, height)
			case 'terrain':
				terrain_tile_list = import_cut_graphics('./assets/world/tiles/tileset.png')
				tile_surface = terrain_tile_list[int(val)]
				sprite = StaticTile(self.game, TILE_SIZE, x , y, tile_surface)
				return sprite
			case 'foreground':
				terrain_tile_list = import_cut_graphics('./assets/world/tiles/tileset.png')
				tile_surface = terrain_tile_list[int(val)]
				sprite = StaticTile(self.game, TILE_SIZE, x , y, tile_surface)
				return sprite
			case 'background':
				terrain_tile_list = import_cut_graphics('./assets/world/tiles/tileset.png')
				tile_surface = terrain_tile_list[int(val)]
				sprite = StaticTile(self.game, TILE_SIZE, x , y, tile_surface)
				return sprite
			# Add more sprite types as needed
			case _:
				raise ValueError(f"Invalid sprite type: {sprite_type}")
