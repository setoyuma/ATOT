import pygame as pg
import math

from support import *

class Projectile(pg.sprite.Sprite):
	def __init__(self, pos, speed, animation, damage, groups, offset):
		super().__init__(groups)
		self.pos = pos
		print(self.pos)
		self.image = pg.Surface((10,10))
		self.image.fill((255,255,255))
		self.rect = pg.Rect(pos[0], pos[1], 10, 10)
		self.speed = speed
		self.animation = animation
		self.damage = damage

		mx, my = pg.mouse.get_pos()
		print(mx, my)
		print(pos)
		self.dir = (mx - pos[0], my - pos[1])
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)
		print(self.dir)
		print("\n")

		angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

	def update(self, offset):
		self.pos = (self.pos[0]+self.dir[0]*self.speed, 
					self.pos[1]+self.dir[1]*self.speed)
		self.rect.center = self.pos