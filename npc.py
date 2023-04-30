import pygame as pg 
from tile import AnimatedTile
from random import randint

class NPC(AnimatedTile):
	def __init__(self,size,x,y,groups,NPC_type:str):
		path = f'./assets/NPC/Alryn/run'
		super().__init__(size,x,y,groups,f'./assets/NPC/{NPC_type}/run')
		self.rect.y += size - self.image.get_size()[1]
		
		if NPC_type == 'Alryn':
			self.speed = 5
		
	def move(self):
		self.rect.x += self.speed

	def reverse_image(self):
		if self.speed > 0:
			self.image = pg.transform.flip(self.image,True,False)

	def reverse(self):
		self.speed *= -1

	def update(self):
		self.animate()
		self.move()
		self.reverse_image()