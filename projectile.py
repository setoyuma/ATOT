import pygame as pg
import math
from settings import *
from support import *

class Projectile(pg.sprite.Sprite):
	def __init__(self, x, y, mouseX, mouseY, groups):
		super().__init__(groups)
		self.x = x
		self.y = y
		self.mouseX = mouseX
		self.mouseY = mouseY
		self.speed = 15
		self.angle = math.atan2(y-mouseY, x-mouseX)
		self.x_velocity = math.cos(self.angle) * self.speed
		self.y_velocity = math.sin(self.angle) * self.speed

	def main(self, display):
		self.x -= int(self.x_velocity)
		self.y -= int(self.y_velocity)

		pg.draw.circle(display, (0,0,0), (self.x, self.y), 15)


class Bullet(pg.sprite.Sprite):
	def __init__(self, x, y, type, size, group):
		super().__init__(group)
		self.pos = (x, y)
		self.group = group
		self.type = type
		self.size = size
		self.speed = bullet_speed

		mx, my = pg.mouse.get_pos()
		self.dir = (mx - x, my - y)
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)

		self.angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))
		
		# animation 
		self.import_assets()
		self.frame_index = 0
		self.animation = self.animations[self.type]
		self.animation_speed = 0.35
		self.image = self.animations[self.type][self.frame_index]

	def import_assets(self):
		path = f'./assets/player/spells/'
		self.animations = {f'{self.type}':[],}
		
		for animation in self.animations.keys():
			full_path = path + animation
			self.animations[animation] = scale_images(import_folder(full_path), (self.size, self.size))

	def animate(self):
		animation = self.animations[self.type]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0
			
		self.image = pg.transform.rotate(animation[int(self.frame_index)], self.angle)

	def update(self):
		self.pos = (self.pos[0]+self.dir[0]*self.speed, 
					self.pos[1]+self.dir[1]*self.speed)

	def draw(self, surf):
		self.rect = self.image.get_rect(center = self.pos)
		surf.blit(self.image, self.rect)
		self.animate()
		# pg.draw.rect(pg.display.get_surface(), "red", self.rect)

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
