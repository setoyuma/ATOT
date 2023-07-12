""" BLACKFORGE2 """
""" Developed by Setoichi at Savior Systems """
""" (/0_0)/ """
import pygame
import pygame.gfxdraw
import random, sys

from functools import partial
from pygame.locals import *
from os import walk,sep
from csv import reader
from math import *

pygame.font.init()

# IMPORT YOUR SETTINGS FILE
#from settings import *

""" PHYSICS """
class Physics():

	def __init__(self):
		pass
	
	def apply_gravity(self, entity, gravity_value:float, delta_time:float):
		entity.velocity.y += gravity_value * delta_time

	def horizontal_movement_collision(self, entity, sprites_to_check:pygame.sprite.Group):
		entity.collision_area.center = entity.rect.center
		sprites_to_check = [sprite for sprite in sprites_to_check.sprites() if sprite.rect.colliderect(entity.collision_area)]

		for sprite in sprites_to_check:
			if sprite.rect.colliderect(entity.rect):
				if entity.velocity.x < 0:
					entity.rect.left = sprite.rect.right
					entity.collide_left = True
					entity.current_x = entity.rect.left

				if entity.velocity.x > 0:
					entity.rect.right = sprite.rect.left
					entity.collide_right = True
					entity.current_x = entity.rect.right

		if entity.collide_left and (entity.rect.left < entity.current_x or entity.velocity.x >= 0):
			entity.collide_left = False
		if entity.collide_right and (entity.rect.right > entity.current_x or entity.velocity.x <= 0):
			entity.collide_right = False

	def vertical_movement_collision(self, entity, sprites_to_check:pygame.sprite.Group):
		entity.collision_area.center = entity.rect.center
		sprites_to_check = [sprite for sprite in sprites_to_check.sprites() if sprite.rect.colliderect(entity.collision_area)]

		for sprite in sprites_to_check:
			if sprite.rect.colliderect(entity.rect):
				if entity.velocity.y > 0:
					entity.rect.bottom = sprite.rect.top
					entity.velocity.y = 0
					entity.collide_bottom = True
				if entity.velocity.y < 0:
					entity.rect.top = sprite.rect.bottom
					entity.velocity.y = 0
					entity.collide_top = True

		if entity.collide_bottom and entity.velocity.y < 0 or entity.velocity.y > 1:
			entity.collide_bottom = False
		if entity.collide_top and entity.velocity.y > 0.1:
			entity.collide_top = False

""" GAME OBJECTS """
class Entity(pygame.sprite.Sprite):

	def __init__(self, size:int, position:tuple, speed:int, groups:list):
		super().__init__(groups)
		self.speed = speed
		self.velocity = pygame.math.Vector2()
		self.size = pygame.math.Vector2(size, size)
		self.position = pygame.math.Vector2(position)

		self.image = pygame.Surface(self.size)
		self.rect = pygame.Rect(self.position, self.size)

		# physics and state variables
		self.physics = Physics()
		self.collide_left = False
		self.collide_right = False
		self.collide_top = False
		self.collide_bottom = False
		self.facing_right = True

	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.rect.topleft)

	def update(self):
		pass

class StaticTile(pygame.sprite.Sprite):
	def __init__(self, position:tuple, groups:list, surface:pygame.Surface):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft=position)
		self.position = pygame.math.Vector2(position)  # Initial position of the tile

	def update(self, world_shift):
		self.rect.x += world_shift.x
		self.rect.y += world_shift.y

class MovingTile(StaticTile):
	def __init__(self, pos:tuple, groups:list, direction:str, speed:int, delta_time:float, surface:pygame.Surface):
		super().__init__(position, groups, surface)
		self.image = surface
		self.delta_time = delta_time
		self.direction = direction  # Movement direction ('up', 'down', 'left', 'right')
		self.speed = speed  # Movement speed (pixels per frame)

	def move(self, constraints:list):
		for constraint in constraints:
			if self.rect.colliderect(constraint.rect):
				if self.direction == 'up':
					print("at top")
					self.direction = "down"
				elif self.direction == 'down':
					print("at bottom")
					self.direction = "up"
				elif self.direction == 'right':
					print("at right")
					self.direction = "left"
				elif self.direction == 'left':
					print("at left")
					self.direction = "right"
			
			if self.direction == 'up':
				self.rect.y -= self.speed * self.delta_time
			elif self.direction == 'down':
				self.rect.y += self.speed * self.delta_time
			elif self.direction == 'left':
				self.rect.x -= self.speed * self.delta_time
			elif self.direction == 'right':
				self.rect.x += self.speed * self.delta_time

class AnimatedTile(StaticTile):
	def __init__(self,size:int,x:int,y:int,path:str):
		super().__init__(size,x,y)
		self.frames = import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

	def animate(self) -> None:
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self) -> None:
		self.animate()

class Light():
	def __init__(self, radius:int, color:str, intensity:float, screen_width:int, screen_height:int, world_brightness:int, manual_pos=(0,0)):
		# Initialize the Light object
		self.position = pygame.math.Vector2(manual_pos)  # Set the position of the light
		self.radius = radius  # Radius of the light
		self.color = color  # Color of the light
		self.intensity = intensity  # Intensity of the light
		self.world_brightness = world_brightness  # Brightness of the world
		self.screen_width = screen_width
		self.screen_height = screen_height


	def generate_glow(self, glow:int, radius:int) -> pygame.Surface:
		# Generate a surface for the light glow effect
		surface = pygame.Surface((int(radius)*2, int(radius)*2), pygame.SRCALPHA)

		layers = 30  # Number of layers for the glow effect

		glow = clamp(glow, 0, 255)  # Clamp the glow intensity
		for i in range(layers):
			pygame.draw.circle(
				surface, self.color, surface.get_rect().center, radius - i * 3
			)
		return surface

	def world_light(self):
		# Create the overlay with the world brightness
		self.light_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)
		self.light_layer.convert_alpha()
		self.light_layer.fill((self.world_brightness, self.world_brightness, self.world_brightness))

	def apply_lighting(self, surface:pygame.Surface, light_layer:pygame.Surface, light_source_list=None) -> None:
		# Apply lighting effects to the given surface

		if self.position.x > 0:
			# If a manual position is set for the light, blit a glow at that position
			# Adjust the position based on the camera offset
			pos_x = self.position.x
			pos_y = self.position.y
			light_layer.blit(self.generate_glow(self.intensity, self.radius*2), (pos_x-100, pos_y-100), special_flags=pygame.BLEND_RGB_ADD)
		else:
			for light_source in light_source_list:
				# Blit a glow for each light source in the light source list
				# Adjust the position based on the camera offset
				pos_x = light_source.rect.centerx
				pos_y = light_source.rect.centery
				light_layer.blit(self.generate_glow(self.intensity, self.radius*2), (pos_x-100, pos_y-100), special_flags=pygame.BLEND_RGB_ADD)

		# Blit the overlay with the glows on the surface
		surface.blit(light_layer, (0,0), special_flags=pygame.BLEND_RGB_MULT)

""" USER INTERFACE """
class Button():
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
			draw_text(self.surf, text=self.text, pos=self.center, size=self.size, color=self.text_color)
		self.game.screen.blit(self.surf, self.rect.topleft)

	def draw_rect(self, rect:pygame.Rect, color:str) -> None:
		pygame.draw.rect(self.surf, color, rect)

	def draw_image(self, image:pygame.Surface, color:str) -> None:
		self.surf.blit(image, (0,0))
	

""" SUPPORT CLASSES """
class Animator():

	def __init__(self, game, animation_speed:int=0.25):
		self.game = game
		self.frame_index = 0
		self.animation_speed = animation_speed
		self.animation = []

	def animate(self, animation:list):
		self.animation = animation
		if self.frame_index < len(animation):
			self.frame_index += self.animation_speed * self.game.dt
		
		if int(self.frame_index) + 1 >= len(animation):
			self.frame_index = 0

	def run(self, animation:list):
		self.animate(animation)

""" SUPPORT FUNCTIONS """
def clamp(num:int, min_value:int, max_value:int):
	return max(min(num, max_value), min_value)

def import_folder(path:str) -> list:	
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

def import_csv_layout(path:str) -> list:
	terrain_map = []
	with open(path) as map:
		level = reader(map, delimiter=',')
		for row in level:
			terrain_map.append(list(row))
		return terrain_map

def import_cut_graphics(path:str, tile_size:int) -> list:
	surface = get_image(path)
	tile_num_x = int(surface.get_size()[0] / tile_size)
	tile_num_y = int(surface.get_size()[1] / tile_size)

	cut_tiles = []
	for row in range(tile_num_y):
		for col in range(tile_num_x):
			x = col * tile_size
			y = row * tile_size
			new_surf = pygame.Surface(
				(tile_size, tile_size), flags=pygame.SRCALPHA)
			new_surf.blit(surface, (0, 0), pygame.Rect(
				x, y, tile_size, tile_size))
			cut_tiles.append(new_surf)

	return cut_tiles

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

_text_library = {}
def draw_text(surface:pygame.Surface, text:str, pos:tuple, font=None, size=30, color=(255,255,255), bg_color=None):
	global _text_library
	text_surf = _text_library.get(f"{text}{color}{size}")
	if text_surf is None:
		usefont = pygame.font.Font(font, size)
		text_surf = usefont.render(text, True, color, bg_color)
		_text_library[f"{text}{color}{size}"] = text_surf
	x, y = pos
	surface.blit(text_surf, (x - (text_surf.get_width() // 2), y - (text_surf.get_height() // 2)))

_image_library = {}
def get_image(path:str):
	global _image_library
	image = _image_library.get(path)
	if image == None:
		canonicalized_path = path.replace('/', sep).replace('\\', sep)
		image = pygame.image.load(canonicalized_path).convert_alpha()
		_image_library[path] = image
	return image

_sound_library = {}
def play_sound(path:str, stop=None):
	global _sound_library
	sound = _sound_library.get(path)
	if sound == None:
		canonicalized_path = path.replace('/', sep).replace('\\', sep)
		sound = pygame.mixer.Sound(canonicalized_path)
		_sound_library[path] = sound
	if stop is None:
		sound.play()
	elif stop:
		sound.stop()
	else:
		sound.play(10)

def scale_images(images: list, size: tuple) -> list:
	""" returns scaled image assets """
	scaled_images = []
	for image in images:
		scaled_images.append(pygame.transform.scale(image, size))
	return scaled_images

def text_line_wrap(surface:pygame.Surface, text:str, color:str, rect:pygame.Rect, font:pygame.Font, aa=False, bkg=None):
	rect = pygame.Rect(rect)
	y = rect.top
	lineSpacing = -2

	# get the height of the font
	fontHeight = font.size("Tg")[1]

	while text:
		i = 1

		# determine if the row of text will be outside our area
		if y + fontHeight > rect.bottom:
			break

		# determine maximum width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1

		# if we've wrapped the text, then adjust the wrap to the last word      
		if i < len(text): 
			i = text.rfind(" ", 0, i) + 1

		# render the line and blit it to the surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)

		surface.blit(image, (rect.left, y))
		y += fontHeight + lineSpacing

		# remove the text we just blitted
		text = text[i:]

	return text

def sine_wave_value() -> int:
	value = sin(pygame.time.get_ticks())
	if value >= 0: 
		return 255
	else: 
		return 0

def palette_swap(image:pygame.Surface, old_color:list, new_color:list) -> pygame.Surface:
	image_copy = pygame.Surface(image.get_size())
	image_copy.fill(new_color)
	image.set_colorkey(old_color)
	image_copy.blit(image, (0, 0))
	return image_copy