import pygame as pg
from constants import *
from tile import Tile,StaticTile
from player import Player
from support import *
from ui import UI
from camera import CameraGroup

class Level:

	def __init__(self,level_data):
		#level setup
		self.displaySurface = pg.display.get_surface()

		# ui
		self.UI = UI(self.displaySurface)

		#sprite group setup
		self.terrain = pg.sprite.Group()
		self.foreground = pg.sprite.Group()
		self.playerLayer = pg.sprite.Group()
		self.activeSprites = pg.sprite.Group() # sprites in here will be updated
		self.collisionSprites = pg.sprite.Group() #sprites that the player can collide with

		# create layers
		self.camera = CameraGroup()
		self.camera.addLayer([
			self.terrain, 
			self.playerLayer,
			self.foreground,
		])

		#terrain layout
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
		
		# foreground layout
		foreground_layout = import_csv_layout(level_data['foreground'])
		self.foreground_sprites = self.create_tile_group(foreground_layout,'foreground')
		
		# player 
		player_layout = import_csv_layout(level_data['player'])
		self.player = pg.sprite.GroupSingle()
		self.goal = pg.sprite.GroupSingle()
		self.player_setup(player_layout)

	def create_tile_group(self,layout,type):
		sprite_group = pg.sprite.Group()

		for row_index, row in enumerate(layout):
				for col_index,val in enumerate(row):
					if val != '-1':
						x = col_index * TILE_SIZE
						y = row_index * TILE_SIZE
						
						if type == 'terrain':
							terrain_tile_list = import_cut_graphics('./assets/terrain/Tileset.png')
							tile_surface = terrain_tile_list[int(val)]
							sprite = StaticTile((x,y),[self.terrain,self.collisionSprites],tile_surface)
						
						if type == 'foreground':
							foreground_tile_list = import_cut_graphics('./assets/terrain/Tileset.png')
							tile_surface = foreground_tile_list[int(val)]
							sprite = StaticTile((x,y),self.foreground,tile_surface)
							# sprite.image = pg.transform.scale(sprite.image, (32,32))
						
						if type == 'constraint':
							sprite = Tile(TILE_SIZE,)
						
						sprite_group.add(sprite)
						
		return sprite_group

	def player_setup(self,layout):
		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					# print(f"Proper Spawn x: {x}")
					# print(f"Proper Spawn y: {y}")
					self.Player = Player((x,y),[self.playerLayer,],self.collisionSprites,self.displaySurface)
					self.player.add(self.Player)
				
	def layerSort(self):
		self.camera.customDraw(self.Player)
		self.playerLayer.update()
		self.collisionSprites.update()

	def run(self):
		self.layerSort()
		# self.UI.show_health(self.Player.hp,100)


	