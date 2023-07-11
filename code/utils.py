from math import sin

from BLACKFORGE2DEV import *
from CONSTANTS import *


""" SUPPORT FUNCTIONS/CLASSES """
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

def draw_custom_font_text(surface:pygame.Surface, letter_dictionary:dict, text:str, text_size:int, position:tuple, split_on:list = []):
	for index, letter in enumerate(text):
			if letter not in split_on:
				scaled_letter = scale_images([letter_dictionary[letter.lower()]], (text_size, text_size))[0]
				surface.blit(scaled_letter, (position[0] + text_size * index, position[1]))

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
