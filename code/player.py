from saviorsystems.REDFORGE import *

class Player(Entity):
	def __init__(self,character:str,pos,surface,group):
		super().__init__(96,pos,CHARACTERS[character]["SPEED"],group)
		self.character = character
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)

		# player movement
		self.velocity = pygame.math.Vector2(0,0)
		self.speed = 8
		self.gravity = 0.8
		self.jump_speed = CHARACTERS[self.character]["JUMPFORCE"]

		# player status
		self.status = 'idle'

	""" PLAYER ASSETS """
	def import_character_assets(self):
		character_path = '../assets/character/'
		self.animations = {'idle':[],'run':[],'jump':[],'fall':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = scale_images(import_folder(full_path), self.size)

	def import_dust_run_particles(self):
		self.dust_run_particles = import_folder('../assets/character/dust_particles/run')

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image,True,False)
			self.image = flipped_image

	""" INPUT/STATE """
	def get_input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d]:
			self.velocity.x = 1
			self.facing_right = True
		elif keys[pygame.K_a]:
			self.velocity.x = -1
			self.facing_right = False
		else:
			self.velocity.x = 0

		if keys[pygame.K_SPACE] and self.collide_bottom:
			self.jump()

	def get_status(self):
		if self.velocity.y < 0:
			self.status = 'jump'
		elif self.velocity.y > 1:
			self.status = 'fall'
		else:
			if self.velocity.x != 0:
				self.status = 'run'
			else:
				self.status = 'idle'

	def jump(self):
		self.velocity.y = self.jump_speed

	""" HITBOXING """
	def hitboxing(self):
		self.hitbox = pygame.Rect( self.position, (self.size.x/2, self.size.y) )

		self.hitbox.center = self.rect.center

	""" UPDATE """
	def update(self, world_shift):
		self.hitboxing()
		self.get_status()
		self.animate()
