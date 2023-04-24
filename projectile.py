import pygame as pg
import math

class Projectile(pg.sprite.Sprite):
	def __init__(self, offsetPos, color, surf):
		self.offsetPos = offsetPos
		mx, my = pg.mouse.get_pos()
		self.dir = (mx - self.offsetPos.x, my - self.offsetPos.y)
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)
		angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))
		self.display_surface = surf
		self.color = color
		self.image = pg.image.load('./assets/spells/fireball/fireball.png')
		# self.rect = self.image.get_rect()
		self.rect = pg.Rect((self.offsetPos.x + 50, self.offsetPos.y + 50), (32,32))
		self.direction = pg.math.Vector2()
		self.speed = 3

	def draw(self):
		self.display_surface.blit(self.image, self.rect)
		# pg.draw.rect(self.display_surface, self.color, self.rect)

	def move(self):
		self.direction.x = self.speed
		self.pos = (self.offsetPos[0]+self.dir[0]*self.speed, self.offsetPos[1]+self.dir[1]*self.speed)
	
	def update(self):
		self.rect.x += self.direction.x * self.speed
		self.rect.y += self.direction.y * self.speed