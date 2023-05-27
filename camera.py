import pygame as pg
from constants import *

class CameraGroup(pg.sprite.Group):
	def __init__(self):
		super().__init__()
		self.displaySurface = pg.display.get_surface()
		self.offset = pg.math.Vector2(0,0)
		self.layers = []

	def addLayer(self, groups):
		self.layers.append(groups)

	def get_offset_pos(self, offsetPos):
		return self.offsetPos

	def customDraw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH//2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT//1.5
		
		 # Check if the offset exceeds the map width
		if self.offset.x < 0:
			self.offset.x = 0
		elif self.offset.x > MAP_WIDTH - SCREEN_WIDTH:
			self.offset.x = MAP_WIDTH - SCREEN_WIDTH

		 # Check if player is above or below half of the map height
		if player.rect.centery < SCREEN_HEIGHT // 2:
			self.offset.y = 0  # Lock the camera's y-offset to the top of the map
		elif player.rect.centery > (MAP_HEIGHT - SCREEN_HEIGHT // 2):
			self.offset.y = MAP_HEIGHT - SCREEN_HEIGHT  # Lock the camera's y-offset to the bottom of the map
		else:
			self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

		for layer in self.layers[0]:
			for sprite in sorted(layer.sprites(), key=lambda sprite: sprite.rect.y):
				self.offsetPos = sprite.rect.topleft - self.offset
				self.displaySurface.blit(sprite.image,self.offsetPos)
				sprite.rect.x = self.offsetPos.x
				sprite.rect.y = self.offsetPos.y
				
				# pg.draw.rect(pg.display.get_surface(), "red", sprite.rect)
		# print(self.get_offset_pos(self.offsetPos))
				


