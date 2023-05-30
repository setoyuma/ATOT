import pygame as pg
from CONSTANTS import *

class Camera:
	def __init__(self, player, scroll_bounds):
		# Initialize the Camera object
		self.display_surface = pg.display.get_surface()  # Get the display surface
		self.player = player  # Reference to the player object
		self.scroll_bounds = scroll_bounds  # Rectangle defining the scroll bounds
		self.layers = []  # List of layers containing sprites
		self.offset = pg.math.Vector2(0, 0)  # Current camera offset
		self.target_offset = pg.math.Vector2(0, 0)  # Target camera offset
		self.interpolation = 0.05  # Interpolation factor for smooth camera movement

	def add_layer(self, layer_list):
		# Add a layer of sprites to the camera
		self.layers = layer_list

	def update_layer(self):
		# Update the positions of the sprites in the layers based on the camera offset
		for layer in self.layers:
			for sprite in layer:
				sprite.rect.x -= self.target_offset.x
				sprite.rect.y -= self.target_offset.y

	def update(self):
		# Update the camera position
		self.update_layer()  # Update the sprite positions based on the camera offset

		# Calculate the desired offset based on player position
		desired_offset_x = self.player.rect.centerx - self.display_surface.get_width() // 2
		desired_offset_y = self.player.rect.centery - self.display_surface.get_height() // 2

		# Limit the desired offset to stay within the scroll bounds
		desired_offset_x = max(min(desired_offset_x, self.scroll_bounds.right - self.display_surface.get_width()), self.scroll_bounds.left)
		desired_offset_y = max(min(desired_offset_y, self.scroll_bounds.bottom - self.display_surface.get_height()), self.scroll_bounds.top)

		# Interpolate the current offset towards the desired offset
		self.offset += (pg.math.Vector2(desired_offset_x, desired_offset_y) - self.offset) * self.interpolation

	def draw(self):
		# Draw the sprites on the screen
		for layer in self.layers:
			for sprite in layer:
				offset_pos = sprite.rect.topleft - self.offset
				self.display_surface.blit(sprite.image, offset_pos)
