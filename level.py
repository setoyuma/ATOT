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
		# ui
		self.UI = UI(self.displaySurface)

		#sprite group setup
		self.terrain = pg.sprite.Group()
		self.lights = pg.sprite.Group()
		self.movingPlats = pg.sprite.Group()
		self.foreground = pg.sprite.Group()
		self.playerLayer = pg.sprite.Group()
		self.activeSprites = pg.sprite.Group() # sprites in here will be updated
		self.collisionSprites = pg.sprite.Group() #sprites that the player can collide with

		# create layers
		self.camera = CameraGroup()
		self.camera.addLayer([
			self.terrain,
			self.lights,
			self.movingPlats, 
			self.playerLayer,
			self.foreground,
		])

		# particles
		# self.particle = ParticlePrinciple((0,0))
		self.particle_system = ParticleSystem()
		self.particle_image = pg.Surface((8,8))
		self.particle_image.fill((0,250,150))
		self.particles = []

		# lights
		self.light_list = []

		# moving platforms
		self.moving_platforms = []

		#terrain layout
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
		
		#lights layout
		self.lights_layout = import_csv_layout(level_data['lights'])
		self.lights_sprites = self.create_tile_group(self.lights_layout,'lights')
		
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
							sprite = StaticTile((x,y),[self.lights,],tile_surface)

	def player_setup(self,layout):
		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.Player = Player((x,y),[self.playerLayer,],self.collisionSprites,self.displaySurface)
					self.player.add(self.Player)

	def light_handler(self, player):
		self.light_list.append(Light((player.rect.x-55, player.rect.y-55), 50, 'white', 100))
		
		for i in range(len(self.lights)):
			self.light_list.append(Light((10*i, 20), 50, 'white', 15))

		for light in self.light_list:
			# light.draw(self.displaySurface)
			light.apply_lighting(self.lights, self.displaySurface)
			break

	def particle_handler(self):
		
		for light in self.lights.sprites():
			self.particles.append(Particle(light.rect.centerx, light.rect.centery, 'up', 3, (255,255,255)))

		for particle in self.particles:
			particle.update()
			particle.draw(self.displaySurface)

		self.particles = [particle for particle in self.particles if not particle.is_expired()]
	
	def platform_handler(self):
		for platform in self.moving_platforms:
			platform.move()
			# pg.draw.rect(self.displaySurface, "white", platform.rect)


	def layerSort(self):
		self.camera.customDraw(self.Player)
		self.playerLayer.update()
		self.collisionSprites.update()
		

	def run(self):
		self.layerSort()
		self.platform_handler()
		self.particle_handler()
		self.light_handler(self.Player)
		# self.UI.show_health(self.Player.hp,100)


	