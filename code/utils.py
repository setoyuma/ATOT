from math import sin

from BLACKFORGE2DEV import *
from CONSTANTS import *


""" SUPPORT FUNCTIONS/CLASSES """
class Cursor:

	def __init__(self, game, cursor:str, size:int):
		self.game = game
		self.size = pygame.math.Vector2(size, size)
		self.image = scale_images([get_image(f'../assets/ui/cursor/{cursor}1.png')], self.size)[0]
		self.position = pygame.math.Vector2(self.game.mx, self.game.my)

	def import_assets(self):
		self.animation_keys = {'':[]} 

		for animation in self.animation_keys:
			full_path = LAUNCHER_ASSET_PATH + animation
			
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = scaled_images

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.stats]
		self.frame_index += self.animation_speed

		if self.frame_index >= len(animation):
			self.frame_index = self.frame_index - 1

		self.image = animation[int(self.frame_index)]

	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.position)

	def update(self):
		pass


def alryn_pallete_swap(image:pygame.Surface, new_blue:list, new_blue_shadow:list, new_gold:list=[], new_skin:list=[], new_skin_shadow:list=[], new_hair:list=[], new_hair_shadow:list=[],):

	new_image = palette_swap(image, ALRYN_COLORS['blue'], new_blue)
	new_image = palette_swap(image, ALRYN_COLORS['blue shadows'], new_blue_shadow)
	if len(new_gold) != 0:
		new_image = palette_swap(image, ALRYN_COLORS['gold'], new_gold)
	if len(new_skin) != 0:
		new_image = palette_swap(image, ALRYN_COLORS['skin'], new_skin)
	if len(new_skin_shadow) != 0:
		new_image = palette_swap(image, ALRYN_COLORS['skin shadows'], new_skin_shadow)
	if len(new_hair) != 0:
		new_image = palette_swap(image, ALRYN_COLORS['hair'], new_hair)
	if len(new_hair_shadow) != 0:
		new_image = palette_swap(image, ALRYN_COLORS['hair shadows'], new_hair_shadow)
	new_image.set_colorkey((0, 0, 0))

	return new_image

_custom_font_text_library = {}
def draw_custom_font_text(surface:pygame.Surface, custom_font:dict, text:str, text_size:int, position:tuple, split_on:list = []):
	global _custom_font_text_library
	text_surf = _custom_font_text_library.get(f"{text}{text_size}")
	if text_surf is None:
		text_surf = pygame.Surface((text_size * len(text), text_size)).convert_alpha()
		text_surf.fill((0,0,0,0))
		for index, letter in enumerate(text):
			if letter not in split_on:
				font_index = ord(letter.lower()) - ord('a')
				scaled_letter = scale_images([custom_font[font_index]], (text_size, text_size))[0]
				text_surf.blit(scaled_letter, (text_size * index, 0))
		_custom_font_text_library[f"{text}{text_size}"] = text_surf
	x, y = position
	surface.blit(text_surf, (x, y))

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
	if entity.entity_type in ["player", "enemy", "item"]:
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
