import pygame as pg
from constants import *
from tile import *
from player import Player
from support import *
from ui import UI
from camera import CameraGroup
from particle import *
from light import Light
class Level:

	def __init__(self,level_data):
		#level setup
		self.displaySurface = pg.display.get_surface()
		self.world_shift = pg.math.Vector2()

		# ui
		self.UI = UI(self.displaySurface)

		#sprite group setup
		self.terrain = pg.sprite.Group()
		self.torches = pg.sprite.Group()
		self.movingPlats = pg.sprite.Group()
		self.foreground = pg.sprite.Group()
		self.playerLayer = pg.sprite.Group()
		self.activeSprites = pg.sprite.Group() # sprites in here will be updated
		self.collisionSprites = pg.sprite.Group() #sprites that the player can collide with

		self.world_layers = [
			self.terrain,
			self.torches,
			self.movingPlats, 
			self.foreground,
		]

		# create layers
		self.camera = CameraGroup()
		self.camera.addLayer([
			self.terrain,
			self.torches,
			self.movingPlats, 
			self.playerLayer,
			self.foreground,
		])

		# particles
		self.particles = []

		# lights
		self.light_list = []

		# moving platforms
		self.moving_platforms = []

		#terrain layout
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
		
		#lights layout
		self.torches_layout = import_csv_layout(level_data['lights'])
		self.torches_sprites = self.create_tile_group(self.torches_layout,'lights')
		
		# foreground layout
		foreground_layout = import_csv_layout(level_data['foreground'])
		self.foreground_sprites = self.create_tile_group(foreground_layout,'foreground')
		
		# movingPlats layout
		movingPlats_layout = import_csv_layout(level_data['movingPlats'])
		self.movingPlats_sprites = self.create_tile_group(movingPlats_layout,'movingPlats')
		
		# player 
		player_layout = import_csv_layout(level_data['player'])
		self.player = pg.sprite.GroupSingle()
		self.goal = pg.sprite.GroupSingle()
		self.player_setup(player_layout)

	def create_tile_group(self,layout,type):
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
						
						if type == 'movingPlats':
							movingPlats_tile_list = import_cut_graphics('./assets/terrain/Tileset.png')
							tile_surface = movingPlats_tile_list[int(val)]
							sprite = MovingTile((x,y),[self.movingPlats, self.collisionSprites],'right', 5, tile_surface)
							self.moving_platforms.append(sprite)
						
						if type == 'constraint':
							sprite = Tile(TILE_SIZE,)
						
						if type == 'lights':
							print("light")
							lights_tile_list = import_cut_graphics('./assets/terrain/Tileset.png')
							tile_surface = lights_tile_list[int(val)]
							sprite = StaticTile((x,y),[self.torches,],tile_surface)

	def player_setup(self,layout):
		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.Player = Player((x,y),[self.playerLayer,],self.collisionSprites,self.displaySurface)
					self.player.add(self.Player)

	def light_handler(self, player):
		self.light_list.append(Light(50, 'white', 15))

		for light in self.light_list:
			light.apply_lighting(self.displaySurface, self.torches)
			break

	def particle_handler(self):
		
		# torch particles
		for torch in self.torches.sprites():
			self.particles.append(Particle(torch.rect.centerx, torch.rect.centery, '', 3, (255,255,255), 'torch'))

		# draw and update particles
		for particle in self.particles:
			particle.update()
			particle.draw(self.displaySurface)

		# particle_light = Light(5, "white", 200, manual_pos=particle.pos)
		# for particle in self.particles:
		# 	particle_light.apply_lighting(self.displaySurface)
		# 	break	

		self.particles = [particle for particle in self.particles if not particle.is_expired()]
	
	def platform_handler(self):
		for platform in self.moving_platforms:
			platform.move()
			# pg.draw.rect(self.displaySurface, "white", platform.rect)

	def draw_layers(self):
		self.camera.customDraw(self.Player)
		
		# for layer in self.world_layers:
		# 	layer.draw(self.displaySurface)

		# self.playerLayer.draw(self.displaySurface)

	def update_layers(self):
		for layer in self.world_layers:
			for sprite in layer.sprites():
				sprite.update(self.world_shift.x, self.world_shift.y)

	def update_sprites(self):
		self.playerLayer.update()
		self.collisionSprites.update()

	def run(self):
		self.draw_layers()
		# self.update_layers()
		self.update_sprites()
		self.platform_handler()
		self.particle_handler()
		self.light_handler(self.Player)
		# self.UI.show_health(self.Player.hp,100)


	