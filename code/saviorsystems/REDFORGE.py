""" REDFORGE """
import pygame
import pygame.gfxdraw
import math, random, sys

from pygame.locals import *
from os import walk,sep
from csv import reader


# IMPORT YOUR SETTINGS FILE
from settings import *

""" PHYSICS """
class Physics():

	def __init__(self):
		pass

	def apply_gravity(self, entity, gravity_value):
		entity.velocity.y += gravity_value
		entity.rect.y += entity.velocity.y

	def horizontal_movement_collision(self, entity, collision_tiles:pygame.sprite.Group):
		entity = entity
		entity.rect.x += entity.velocity.x * entity.speed

		for sprite in collision_tiles.sprites():
			if sprite.rect.colliderect(entity.rect):
				if entity.velocity.x < 0: 
					entity.rect.left = sprite.rect.right
					entity.collide_left = True
					self.current_x = entity.rect.left
				elif entity.velocity.x > 0:
					entity.rect.right = sprite.rect.left
					entity.collide_right = True
					self.current_x = entity.rect.right

		if entity.collide_left and (entity.rect.left < self.current_x or entity.velocity.x >= 0):
			entity.collide_left = False
		if entity.collide_right and (entity.rect.right > self.current_x or entity.velocity.x <= 0):
			entity.collide_right = False

	def vertical_movement_collision(self, entity, collision_tiles:pygame.sprite.Group):
		entity = entity
		for sprite in collision_tiles.sprites():
			if sprite.rect.colliderect(entity.rect):
				if entity.velocity.y > 0: 
					entity.rect.bottom = sprite.rect.top
					entity.velocity.y = 0
					entity.collide_bottom = True
				elif entity.velocity.y < 0:
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
	def __init__(self, pos:tuple, groups:list, surface:pygame.Surface):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft=pos)
		self.pos = pygame.math.Vector2(pos)  # Initial position of the tile

	def update(self, world_shift):
		self.rect.x += world_shift.x
		self.rect.y += world_shift.y

class MovingTile(StaticTile):
	def __init__(self, pos:tuple, groups:list, direction:str, speed:int, surface:pygame.Surface):
		super().__init__(pos, groups, surface)
		self.image = surface
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
				self.rect.y -= self.speed
			elif self.direction == 'down':
				self.rect.y += self.speed
			elif self.direction == 'left':
				self.rect.x -= self.speed
			elif self.direction == 'right':
				self.rect.x += self.speed

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

class Particle():
	def __init__(self, x:int, y:int, direction:str, velocity:int, color:str, type=None, radius=5, fill=True):
		# Initialize the Particle object
		self.pos = pygame.math.Vector2(x, y)  # Position vector of the particle
		self.vel = pygame.math.Vector2(0, 0)  # Velocity vector of the particle
		self.type = type  # Type of the particle
		self.timer = None  # Timer for the particle's lifespan
		self.set_direction(direction, velocity)  # Set the direction and velocity of the particle
		self.fill = fill	# Should the particle be filled with a color
		self.color = color  # Color of the particle
		self.radius = radius  # Radius of the particle based on the timer value

	def random_direction(self, start_angle_degrees:int, end_angle_degrees:int):
		# Generate a random direction vector within the specified angle range
		angle_degrees = random.uniform(start_angle_degrees, end_angle_degrees)
		angle_radians = math.radians(angle_degrees)
		dx = math.cos(angle_radians) * random.randint(0,1) 
		dy = math.sin(angle_radians) * random.randint(0,1)
		return dx, dy

	def set_type(self) -> str:
		# Set the particle's type and return the direction
		match self.type:
			case 'torch':
				direction = 'up'  # For 'torch' type, set direction as 'up'
				self.timer = random.uniform(1, 3)  # Timer for the particle's lifespan
			case _:
				direction = 'up'  # For other types, set direction as 'right'
				self.timer = random.uniform(1, 3)  # Timer for the particle's lifespan
		return direction

	def set_direction(self, direction:str, velocity:int):
		# Set the direction and velocity of the particle
		direction = self.set_type()  # Determine the direction based on the particle's type
		match direction:
			case "up":
				self.vel.y = -velocity  # Set the upward velocity
				if self.type == 'torch':
					self.vel.x = random.randint(-5, 5)  # Set the upward velocity
			
			case "down":
				self.vel.y = velocity  # Set the downward velocity
			
			case "left":
				self.vel.x = -velocity  # Set the leftward velocity
			
			case "right":
				self.vel.x = velocity  # Set the rightward velocity
	
	def emit(self, camera):
		# Move and draw the particle
		dx, dy = self.random_direction(50, 90)  # Generate a random direction vector between 50 and 90 degrees
		# dx = random.randint(-3, 3) 
		# dy = random.randint(-3, 3) 

		self.pos.x += (dx * self.vel.x) + camera.level.world_shift.x  # Update the x-position based on the direction and velocity
		self.pos.y += (dy * self.vel.y) + camera.level.world_shift.y  # Update the y-position based on the direction and velocity
		self.timer -= 0.1  # Decrease the timer by 0.1 to track the particle's lifespan

		self.radius -= 0.1  # Shrink the particle by decreasing the radius
		# self.radius = int(self.timer)  # Update the radius based on the timer value

	def update(self, camera):
		# Update the particle's position and properties over time
		self.emit(camera)  # Emit the particle (move and shrink)

	def draw(self, surface:pygame.Surface, camera):
		# Draw the particle on the screen
		for i in range(int(self.radius), 0, -2):
			alpha = int((i / self.radius) * 255)
			color = self.color + (alpha,)
			if self.fill:
				# Adjust the position based on the camera offset
				pos_x = self.pos.x - camera.level.world_shift.x
				pos_y = self.pos.y - camera.level.world_shift.y
				pygame.gfxdraw.aacircle(surface, int(pos_x), int(pos_y), i, color)
				pygame.gfxdraw.filled_circle(surface, int(pos_x), int(pos_y), i, color)
			else:
				# Adjust the position based on the camera offset
				pos_x = self.pos.x - camera.level.world_shift.x
				pos_y = self.pos.y - camera.level.world_shift.y
				pygame.gfxdraw.aacircle(surface, int(pos_x), int(pos_y), i, color)

	def is_expired(self):
		# Check if the particle's timer has expired
		return self.timer <= 0

class Light():
	def __init__(self, radius:int, color:str, intensity:float, manual_pos=(0,0)):
		# Initialize the Light object
		self.position = pygame.math.Vector2(manual_pos)  # Set the position of the light
		self.radius = radius  # Radius of the light
		self.color = color  # Color of the light
		self.intensity = intensity  # Intensity of the light
		self.world_brightness = WORLD_BRIGHTNESS  # Brightness of the world

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
		self.light_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
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
class Camera():
	def __init__(self, layers:list, player, level):
		self.player = player
		self.level = level
		self.layers = layers

	def add_layer(self, layer:pygame.sprite.Group):
		self.layers.append(layer)

	def scroll_x(self):
		player = self.player
		player_x = player.rect.centerx
		velocity_x = player.velocity.x

		
		if player_x < screen_width / 4 and velocity_x < 0 and self.level.level_topleft.left < 0:
			self.level.world_shift.x = CHARACTERS[player.character]["SPEED"]
			player.speed = 0
		elif player_x > screen_width - (screen_width / 4) and velocity_x > 0 and self.level.level_bottomright.right > SCREEN_WIDTH:
			self.level.world_shift.x = -CHARACTERS[player.character]["SPEED"]
			player.speed = 0
		else:
			self.level.world_shift.x = 0
			player.speed = CHARACTERS[player.character]["SPEED"]

	# im not sure why it doesnt work as intended
	def scroll_y(self):
		player = self.player
		player_y = player.rect.centery
		velocity_y = player.velocity.y

		if player_y < screen_height / 4 and velocity_y < 0:
			self.level.world_shift.y = 8
		elif player_y > screen_height - (screen_height / 4) and velocity_y > 0:
			self.level.world_shift.y = -8
		else:
			self.level.world_shift.y = 0

	def update_layers(self, world_shift:pygame.math.Vector2()):
		for layer in self.layers:
			layer.update(world_shift)

	def draw_layers(self, surface:pygame.Surface):
		for layer in self.layers:
			layer.draw(surface)

	def update(self):
		self.update_layers(self.level.world_shift)

class Button():
	def __init__(self, game, text:str, pos:tuple, function, base=(0,0,300,81), hovered=(0,0,300,81), base_color=(77,77,255,50), hover_color=(77, 77, 80), text_color=(255,255,255), text_size=60, hovered_pos=None, id=None):
		self.game = game
		self.text = text
		self.pos = pos
		self.id = id
		self.function = function
		if isinstance(base, str):
			self.base = pygame.transform.scale(get_image(base), (128,64))
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
			self.hovered = pygame.transform.scale(get_image('../assets/ui/buttons/button_plate2.png'), (128,64))
			self.hover_func = self.draw_image
		else:
			self.hovered = pygame.Rect(hovered)
			self.hover_func = self.draw_rect

		self.rect.center = self.pos
		self.text_color = text_color
		self.base_color = base_color
		self.hover_color = hover_color
		self.size = text_size
		if hovered_pos is None:
			self.hovered_pos = pos
		else:
			self.hovered_pos = hovered_pos
		self.is_hovered = False
	
	def update(self, event:pygame.event) -> None:
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos[0], pos[1]):
			self.is_hovered = True
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

""" SUPPORT CLASSES """
class Animator():
	def __init__(self, game, animation, frame_duration, loop=False):
		self.game = game
		self.animation = animation
		self.frame_duration = frame_duration
		self.current_time = 0
		self.frame_index = 0
		self.loop = loop
		self.done = False

	def update(self, dt:float):
		# add time in ms since last frame
		self.current_time += dt

		# when cumulative time reaches the frame_duration
		if self.current_time > self.frame_duration:

			if self.frame_index >= len(self.animation) - 1:

				# set the flag for an animation that should not repeat
				if not self.loop:
					self.done = True
				else:
					self.frame_index = 0

			else:
				self.frame_index += 1

			# reset the cumulative time for the next frame
			self.current_time = 0

		# return the current frame of the animation list
		return self.animation[self.frame_index]

	def reset(self):
		self.current_time = 0
		self.frame_index = 0
		self.done = False

""" SUPPORT FUNCTIONS """
def clamp(num:int, min_value:int, max_value:int):
	return max(min(num, max_value), min_value)

def import_folder(path:str) -> list:	
	surface_list = []
	for _, __, image_files in walk(path):
		for image in image_files:
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

def import_cut_graphics(path:str) -> list:
	surface = get_image(path)
	tile_num_x = int(surface.get_size()[0] / TILE_SIZE)
	tile_num_y = int(surface.get_size()[1] / TILE_SIZE)

	cut_tiles = []
	for row in range(tile_num_y):
		for col in range(tile_num_x):
			x = col * TILE_SIZE
			y = row * TILE_SIZE
			new_surf = pygame.Surface(
				(TILE_SIZE, TILE_SIZE), flags=pygame.SRCALPHA)
			new_surf.blit(surface, (0, 0), pygame.Rect(
				x, y, TILE_SIZE, TILE_SIZE))
			cut_tiles.append(new_surf)

	return cut_tiles

_text_library = {}
def draw_text(surface:pygame.Surface, text:str, pos:tuple, size=30, color=(255,255,255), bg_color=None):
	global _text_library
	text_surf = _text_library.get(f"{text}{color}{size}")
	if text_surf is None:
		font = pygame.font.Font(None, size)
		text_surf = font.render(text, True, color, bg_color)
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

