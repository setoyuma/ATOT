import pygame as pg
import pygame.gfxdraw
import random
import math
import sys

from support import import_folder, scale_images

class Particle:
	def __init__(self, x, y, direction, velocity, color, type=None, radius=5, fill=True):
		# Initialize the Particle object
		self.pos = pg.math.Vector2(x, y)  # Position vector of the particle
		self.vel = pg.math.Vector2(0, 0)  # Velocity vector of the particle
		self.type = type  # Type of the particle
		self.timer = None  # Timer for the particle's lifespan
		self.set_direction(direction, velocity)  # Set the direction and velocity of the particle
		self.fill = fill	# Should the particle be filled with a color
		self.color = color  # Color of the particle
		self.radius = radius  # Radius of the particle based on the timer value

	def random_direction(self, start_angle_degrees, end_angle_degrees):
		# Generate a random direction vector within the specified angle range
		angle_degrees = random.uniform(start_angle_degrees, end_angle_degrees)
		angle_radians = math.radians(angle_degrees)
		dx = math.cos(angle_radians) * random.randint(0,3)
		dy = math.sin(angle_radians) * random.randint(0,3)
		return dx, dy

	def set_type(self):
		# Set the particle's type and return the direction
		match self.type:
			case 'torch':
				direction = 'up'  # For 'torch' type, set direction as 'up'
				self.timer = random.uniform(1, 3)  # Timer for the particle's lifespan

			case _:
				direction = 'right'  # For other types, set direction as 'right'
		return direction

	def set_direction(self, direction, velocity):
		# Set the direction and velocity of the particle
		direction = self.set_type()  # Determine the direction based on the particle's type
		match direction:
			case "up":
				self.vel.y = -velocity  # Set the upward velocity
			
			case "down":
				self.vel.y = velocity  # Set the downward velocity
			
			case "left":
				self.vel.x = -velocity  # Set the leftward velocity
			
			case "right":
				self.vel.x = velocity  # Set the rightward velocity
	
	def emit(self):
		# Move and draw the particle
		dx, dy = self.random_direction(50, 90)  # Generate a random direction vector between 50 and 90 degrees
		# dx = random.randint(-3, 3) 
		# dy = random.randint(-3, 3) 

		self.pos.x += dx * self.vel.x  # Update the x-position based on the direction and velocity
		self.pos.y += dy * self.vel.y  # Update the y-position based on the direction and velocity
		self.timer -= 0.1  # Decrease the timer by 0.1 to track the particle's lifespan

		self.radius -= 0.1  # Shrink the particle by decreasing the radius
		# self.radius = int(self.timer)  # Update the radius based on the timer value

	def update(self):
		# Update the particle's position and properties over time
		self.emit()  # Emit the particle (move and shrink)

	def draw(self, screen):
		# Draw the particle on the screen
		for i in range(int(self.radius), 0, -2):
			alpha = int((i / self.radius) * 255)
			color = self.color + (alpha,)
			if self.fill:
				pg.gfxdraw.aacircle(screen, int(self.pos.x), int(self.pos.y), i, color)
				pg.gfxdraw.filled_circle(screen, int(self.pos.x), int(self.pos.y), i, color)
			else:
				pg.gfxdraw.aacircle(screen, int(self.pos.x), int(self.pos.y), i, color)

	def is_expired(self):
		# Check if the particle's timer has expired
		return self.timer <= 0


