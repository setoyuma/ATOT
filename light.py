import pygame as pg
from constants import *
from support import *

class Light:
	def __init__(self, radius, color, intensity, manual_pos=(0,0)):
		# Initialize the Light object
		self.position = pg.math.Vector2(manual_pos)  # Set the position of the light
		self.radius = radius  # Radius of the light
		self.color = color  # Color of the light
		self.intensity = intensity  # Intensity of the light
		self.world_brightness = WORLD_BRIGHTNESS  # Brightness of the world

	def generate_glow(self, number_of_lights, glow, radius) -> pg.Surface:
		# Generate a surface for the light glow effect
		surf = pg.Surface((radius*2, radius*2), pg.SRCALPHA)

		layers = 30  # Number of layers for the glow effect

		glow = clamp(glow, 0, 255)  # Clamp the glow intensity
		for i in range(layers):
			k = i * glow
			k = clamp(k, 0, 255)
			pg.draw.circle(
				surf, (k, k, k), surf.get_rect().center, radius - i * 3
			)

		return surf

	def apply_lighting(self, surface, camera, light_source_list=None):
		# Apply lighting effects to the given surface

		# Create the overlay with the world brightness
		overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA, 32)
		overlay.convert_alpha()
		overlay.fill((self.world_brightness, self.world_brightness, self.world_brightness))

		if self.position.x > 0:
			# If a manual position is set for the light, blit a glow at that position
			# Adjust the position based on the camera offset
			pos_x = self.position.x - camera.offset.x
			pos_y = self.position.y - camera.offset.y
			overlay.blit(self.generate_glow(1, self.intensity, self.radius*2), (pos_x-100, pos_y-100), special_flags=pg.BLEND_RGB_ADD)
		else:
			for light_source in light_source_list:
				# Blit a glow for each light source in the light source list
				# Adjust the position based on the camera offset
				pos_x = light_source.rect.centerx - camera.offset.x
				pos_y = light_source.rect.centery - camera.offset.y
				overlay.blit(self.generate_glow(len(light_source_list), self.intensity, self.radius*2), (pos_x-100, pos_y-100), special_flags=pg.BLEND_RGB_ADD)

		# Blit the overlay with the glows on the surface
		surface.blit(overlay, (0,0), special_flags=pg.BLEND_RGB_MULT)
