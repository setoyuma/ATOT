import pygame as pg

from camera import YSortCamera, NoSortCamera
from player_stat_line import StatLine
from projectile import Bullet
from player import Player
from ui import UI
from settings import *
from support import *
from tile import *
from npc import NPC
from item import Item

class World:
	def __init__(self, world_data, player_data, surface, game):
		self.display_surface = surface
		self.game = game
		self.item_list = []
		# UI
		self.ui = UI(self.display_surface)

		# sprite group setup
		self.NOSORT = NoSortCamera()
		self.YSORT = YSortCamera()
		self.NPCSprites = YSortCamera()
		self.playerSprites = YSortCamera()
		self.constraintSprites = YSortCamera()
		self.terrainSprites = NoSortCamera()
		self.projectileSprites = YSortCamera() 
		self.activeSprites = pg.sprite.Group() # these sprites are updated
		self.collisionSprites = pg.sprite.Group() # sprites with collision

		# ground layout
		ground_layout = import_csv_layout(world_data['ground'])
		self.ground_sprites = self.create_tile_group(
			ground_layout, 'ground')
		
		# player
		player_layout = import_csv_layout(world_data['player'])
		self.player = pg.sprite.GroupSingle()
		self.player_setup(player_layout, player_data)

		# enemy setup
		'''NPC'''
		NPC_layout = import_csv_layout(world_data['NPC'])
		self.NPC_sprites = self.create_tile_group(
			NPC_layout,'NPC')

		# terrain layout
		terrain_layout = import_csv_layout(world_data['terrain'])
		self.terrain_sprites = self.create_tile_group(
			terrain_layout, 'terrain')
		
		# constraint
		constraint_layout = import_csv_layout(world_data['constraint'])
		self.constraint_sprites = self.create_tile_group(constraint_layout,'constraint')

		# tree layout
		items_layout = import_csv_layout(world_data['items'])
		self.items_sprites = self.create_tile_group(
			items_layout, 'items')
		
		# tree layout
		tree_layout = import_csv_layout(world_data['trees'])
		self.tree_sprites = self.create_tree_group(
			tree_layout, 'trees')

	def create_tree_group(self, layout, type):
		sprite_group = self.YSORT

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
	
					if type == 'trees' and val == '0':
						deco_list = get_image(
							'./assets/tiles/deco/trees/tree.png')
						deco_surface = deco_list
						sprite = StaticTile(TILE_SIZE, x, y, deco_surface, [self.YSORT])
					
					if type == 'trees' and val == '1':
						deco_list = get_image(
							'./assets/tiles/deco/trees/abborath_tree.png')
						deco_surface = deco_list
						sprite = StaticTile(TILE_SIZE, x, y, deco_surface, [self.YSORT])
					
					if type == 'trees' and val == '2':
						deco_list = get_image(
							'./assets/tiles/deco/trees/tree2.png')
						deco_surface = deco_list
						sprite = StaticTile(TILE_SIZE, x, y, deco_surface, [self.YSORT])
					
					sprite_group.add(sprite)
		return sprite_group

	def create_tile_group(self, layout, type):

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE
					
					if type == 'constraint':
						sprite = Tile(TILE_SIZE,x,y, self.NOSORT)
						self.constraintSprites.add(sprite)

					if type == 'terrain':
						terrain_tile_list = import_cut_graphics(
							'./assets/tiles/tileset.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(TILE_SIZE, x, y, tile_surface, [self.terrainSprites, self.collisionSprites])
						self.terrainSprites.add(sprite)
					
					if type == 'ground':
						ground_tile_list = import_cut_graphics(
							'./assets/tiles/tileset.png')
						ground_surface = ground_tile_list[int(val)]
						sprite = StaticTile(TILE_SIZE, x, y, ground_surface, [self.NOSORT])
						self.NOSORT.add(sprite)

					if type == 'NPC':
						npc = NPC((x,y), 64, "GyrethII", self.NPCSprites)
						self.NPCSprites.add(npc)
						npc.patrol()
						# sprite = NPC(TILE_SIZE,x,y,"Alryn")

					if type == 'items':
						item = Item((x,y), self.Player, self.NOSORT)
						self.NOSORT.add(item)
						self.item_list.append(item)


	def player_setup(self, layout, player_data):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				
				if val == '0':
					self.Player = Player(self.game, player_data, (x, y), [self.playerSprites, self.activeSprites], self.collisionSprites, self.display_surface)
					self.playerSprites.add(self.player)
				
				if val == '1':
					pass
	
	def NPC_collision_reverse(self):
		for npc in self.NPCSprites.sprites():
			for constraint in self.constraintSprites:
				if npc.rect.colliderect(constraint.rect):
					npc.reverse()
					npc.hit_constraint = True
					print('npc hit constraint')  

	def item_pickup(self):
		for item in self.item_list:
			if self.Player.rect.colliderect(item.rect):
				print('touched item')
				self.Player.items.append(item.image)
				item.kill()
				break
		pg.draw.rect(self.display_surface, "purple", item.rect)

	def projectileCollisions(self):
		for sprite in self.terrainSprites.sprites():
			for proj in self.Player.projectiles:
				if proj.rect.colliderect(sprite.rect):
					self.Player.projectiles.remove(proj)
					proj.kill()
		
	def projectile_handler(self):
		if self.Player.casting_projectile:
			proj = Bullet(self.Player.rect.centerx, self.Player.rect.centery, self.Player.projectile_type, self.projectileSprites)
			# proj = Bullet(self.game.player.groups[0].offsetPos.x + 35, self.game.player.groups[0].offsetPos.y + 40, self.Player.projectile_type, self.projectileSprites)
			self.projectileSprites.add(proj)
			self.Player.projectiles.append(proj)
			self.Player.casting_projectile = False		
	
		for proj in self.Player.projectiles:
			proj.draw(self.display_surface)
			# delete projectiles when offscreen
			if not self.display_surface.get_rect().collidepoint((proj.pos[0], proj.pos[1])):
				self.Player.projectiles.remove(proj)

	def layer_sort(self):
		self.NOSORT.customDraw(self.Player)
		# self.YSORT.customDraw(self.Player)
		self.NPCSprites.customDraw(self.Player)
		self.terrainSprites.customDraw(self.Player)
		self.playerSprites.customDraw(self.Player)
		self.NPCSprites.update()
		self.YSORT.update()
		self.projectileSprites.update()
		self.playerSprites.update()
		self.collisionSprites.update()
		

	def run(self):
		self.layer_sort()
		self.projectile_handler()
		self.projectileCollisions()
		self.item_pickup()
		self.NPC_collision_reverse()
		# pg.draw.rect(self.display_surface, "blue", self.Player.rect)
		
		self.stat_line = StatLine("", 25, self.Player, (self.playerSprites.offsetPos.x + 50, self.playerSprites.offsetPos.y- 15), "white", self.display_surface)
		self.stat_line.update()

		self.ui.show_health(self.Player.hp, 100)
		self.ui.show_mana(self.Player.mana, 100)
		self.ui.draw_mini_map(self.Player.stats)


