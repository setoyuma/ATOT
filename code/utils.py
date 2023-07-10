from math import sin

from BLACKFORGE2 import *
from CONSTANTS import *


""" SUPPORT FUNCTIONS/CLASSES """
class Animator():

	def __init__(self, game, target:Entity, animation_speed:int=0.25):
		self.game = game
		self.frame_index = 0
		self.animation_speed = animation_speed
		self.target = target
		self.animation = []

	def animate(self, animation:list):
		self.animation = animation
		if self.frame_index < len(animation):
			self.frame_index += self.animation_speed * self.game.dt
		
		if int(self.frame_index) + 1 >= len(animation):
			self.frame_index = 0

		if self.target.facing_right:
			self.target.image = pygame.transform.scale(animation[int(self.frame_index)], self.target.size)
		else:
			self.target.image = pygame.transform.flip(pygame.transform.scale(animation[int(self.frame_index)], self.target.size), True, False)

		# self.target.image = pygame.transform.scale(animation[int(self.frame_index)], self.target.size)
	
	def run(self, animation:list):
		self.animate(animation)
	

class NewButton():
	def __init__(self, game, size:tuple, text:str, position:tuple, function, base=(0,0,96,96), hovered=(0,0,96,96), base_color=(77,77,255,50), hover_color=(77, 77, 80), text_color=(255,255,255), text_size=60, hovered_pos=None, id=None):
		self.game = game
		self.text = text
		self.position = position
		self.id = id
		self.function = function
		self.clicked = False

		if isinstance(base, str):
			self.base = pygame.transform.scale(get_image(base), size)
			self.rect = self.base.get_rect()
		else:
			self.base = base
			self.rect = base

		if isinstance(base, str):
			self.surf = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA)
			self.base_func = self.draw_image
		else:
			self.base = pygame.Rect(base)
			self.rect = self.base.copy()
			self.surf = pygame.Surface((base[2], base[3]), pygame.SRCALPHA)
			self.base_func = self.draw_rect
		self.center = self.surf.get_rect().center

		if isinstance(hovered, str):
			self.hovered = pygame.transform.scale(get_image(hovered), size)
			self.hover_func = self.draw_image
		else:
			self.hovered = pygame.Rect(hovered)
			self.hover_func = self.draw_rect

		self.rect.center = self.position
		self.text_color = text_color
		self.base_color = base_color
		self.hover_color = hover_color
		self.size = text_size
		if hovered_pos is None:
			self.hovered_pos = position
		else:
			self.hovered_pos = hovered_pos
		self.is_hovered = False
	
	def update(self, event:pygame.event) -> None:
		position = pygame.mouse.get_pos()
		if self.rect.collidepoint(position[0], position[1]):
			self.is_hovered = True
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				self.clicked = True
				#play_sound("Assets/sounds/click.mp3")
				
				if isinstance(self.function, type):
					self.game.sceneManager.scene = self.function(self.game)
					return

				if self.function != None:
						if self.function == pygame.quit:
							self.function()
							sys.exit()
						elif self.id is not None:
							self.function(self.id)
						else:
							self.function()
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				self.clicked = False         
		else:
			self.is_hovered = False

	def draw(self) -> None:
		self.surf.fill((0,0,0,0))
		if self.is_hovered:
			self.hover_func(self.hovered, self.hover_color)
		else:
			self.base_func(self.base, self.base_color)
		if self.text:
			draw_text(self.surf, self.text, self.center, self.size, self.text_color)
		self.game.screen.blit(self.surf, self.rect.topleft)

	def draw_rect(self, rect:pygame.Rect, color:str) -> None:
		pygame.draw.rect(self.surf, color, rect)

	def draw_image(self, image:pygame.Surface, color:str) -> None:
		self.surf.blit(image, (0,0))
	

def new_import_folder(path:str) -> list:	
	surface_list = []
	file_list = []
	for _, __, image_files in walk(path):
		for index, image in enumerate(image_files):
			file_list.append(image)

		# sort images based on numerical values in the image names: run1.png will always come before run12.png as walk doesnt sort files returned.
		file_list.sort(key=lambda image: int(''.join(filter(str.isdigit, image))))
		
		for index, image in enumerate(file_list):
			full_path = path + '/' + image
			image_surf =get_image(full_path).convert_alpha()
			surface_list.append(image_surf)
	
	return surface_list

def draw_custom_font_text(surface:pygame.Surface, letter_dictionary:dict, text:str, text_size:int, position:tuple, split_on:list = []):
	for index, letter in enumerate(text):
			if letter not in split_on:
				scaled_letter = scale_images([letter_dictionary[letter.lower()]], (text_size, text_size))[0]
				surface.blit(scaled_letter, (position[0] + text_size * index, position[1]))

_sound_library = {}
def play_sound(path, stop=None):
	global _sound_library
	sound = _sound_library.get(path)
	if sound == None:
		canonicalized_path = path.replace('/', sep).replace('\\', sep)
		sound = pygame.mixer.Sound(canonicalized_path)
		sound.set_volume(0.3)
		_sound_library[path] = sound
	if stop is None:
		sound.play()
	elif stop:
		sound.stop()
	else:
		sound.play(6)

def tile_collision_test(rect:pygame.Rect, tiles:list) -> list:
	""" Returns a list of tiles the given rect is colliding with """
	tiles_collided_with = []

	for tile in tiles:
		for tile_num, tile_rect in enumerate(tile):
			if rect.colliderect(tile[tile_num]):
				tiles_collided_with.append(tile[tile_num])
	
	return tiles_collided_with

def collision_adjust(entity, velocity:pygame.math.Vector2, dt:float, tiles:list):
	collision_types = {
		'top': False,
		'bottom': False,
		'right': False,
		'left': False,
	}

	rect = entity.rect

	# x axis
	rect.x += velocity.x * dt
	tiles_collided_with = tile_collision_test(rect, [tiles])
	for tile in tiles_collided_with:
		if velocity.x > 0:
			collision_types['right'] = True
			rect.right = tile.left
		elif velocity.x < 0:
			collision_types['left'] = True
			rect.left = tile.right
	
	# adjust the entity based on gravity before checking vertical collisions
	if entity.entity_type in ['player', 'enemy', 'item']:
		entity.physics.apply_gravity(entity, GRAVITY, entity.game.dt)

	# y axis
	rect.y += velocity.y * dt
	tiles_collided_with = tile_collision_test(rect, [tiles])
	for tile in tiles_collided_with:
		if velocity.y > 0:
			rect.bottom = tile.top
			collision_types['bottom'] = True
			entity.collide_bottom = True
		elif velocity.y <= 0:
			rect.top = tile.bottom
			collision_types['top'] = True
			entity.collide_top = True
	
	# check for bumping head
	if collision_types['top'] and velocity.y < 1:
		velocity.y = 0
		
	return rect, collision_types

def glow_surface(radius, color, intensity) -> pygame.Surface:
	intensity = intensity/100
	surface = pygame.Surface((int(radius) * 2, int(radius) * 2), pygame.SRCALPHA)
	surface.convert_alpha()
	pygame.draw.circle(surface, [intensity * value for value in color], (radius, radius), radius)
	surface.set_colorkey([0,0,0])
	return surface

def sine_wave_value() -> int:
	value = sin(pygame.time.get_ticks())
	if value >= 0: 
		return 255
	else: 
		return 0
