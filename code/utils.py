from math import sin

from BLACKFORGE2 import *
from CONSTANTS import *


""" SUPPORT FUNCTIONS/CLASSES """
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
			rect.right = tile.left
			collision_types['right'] = True
		elif velocity.x < 0:
			rect.left = tile.right
			collision_types['left'] = True
	
	# adjust the entity based on gravity before checking vertical collisions
	entity.physics.apply_gravity(entity, GRAVITY, entity.game.dt)

	# y axis
	rect.y += velocity.y * dt
	tiles_collided_with = tile_collision_test(rect, [tiles])
	for tile in tiles_collided_with:
		if velocity.y <= 0:
			rect.top = tile.bottom
			collision_types['top'] = True
			entity.collide_top = True
		elif velocity.y > 0:
			rect.bottom = tile.top
			collision_types['bottom'] = True
			entity.collide_bottom = True
	
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
