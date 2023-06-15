from BLACKFORGE2 import *

from CONSTANTS import *

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
