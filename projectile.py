import pygame as pg
import math
from settings import *
from support import *
class Bullet(pg.sprite.Sprite):
	def __init__(self, x, y, type, group):
		super().__init__(group)
		self.pos = (x, y)
		self.group = group
		self.type = type

		mx, my = pg.mouse.get_pos()
		self.dir = (mx - x, my - y)
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)

		angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

		self.image = get_image(f'./assets/spells/{type}/{type}1.png')
		scaled_bullet = pg.transform.scale(self.image, (64,64))

		self.image = pg.transform.rotate(scaled_bullet, angle)
		self.speed = bullet_speed

	def import_assets(self):
		path = f'./assets/spells/{self.type}/'
		self.animations = {'idle':[],}
		
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = scale_images(import_folder(full_path), (self.size, self.size))
			# print(self.animations[animation])

	def animate(self):
		animation = self.animations[self.status]
		# self.hitbox = pg.Rect((self.groups[0].offsetPos.x + 20, self.groups[0].offsetPos.y), (60,98))

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0
			
		self.image = animation[int(self.frame_index)]
		if not self.facing_right:
			self.image = pg.transform.flip(self.image,True,False)

	def update(self):
		self.pos = (self.pos[0]+self.dir[0]*self.speed, 
					self.pos[1]+self.dir[1]*self.speed)

	def draw(self, surf):
		self.rect = self.image.get_rect(center = self.pos)
		surf.blit(self.image, self.rect)
		pg.draw.rect(pg.display.get_surface(), "red", self.rect)

class RadialBullet():

	def __init__(self, x, y, count):
		self.x = x
		self.y = y
		self.proj = []
		self.count = count
		self.direction = pg.math.Vector2()
		self.image = get_image('./assets/spells/fireball/fireball.png')
		self.rect = self.image.get_rect(topleft=(self.x,self.y))
		self.speed = bullet_speed
		
		
			# [proj.image == pg.transform.rotate(proj.image, angle) for proj in self.proj]

	def on_hit(self):
		self.__init__((self.x, self.y), self.count)

	def draw(self):
		angle = 360/self.count
		for i in range(self.count):
			self.proj.append(self)
			for proj in self.proj:
				pg.display.get_surface().blit(self.image, self.rect)

	def update(self):
		self.direction.x = 1
		self.rect.x += self.direction.x * self.speed		
		self.rect.y += self.direction.y * self.speed		
