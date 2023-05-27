import pygame as pg
import pygame.gfxdraw
import random
import math
import sys

from support import import_folder, scale_images

class ParticlePrinciple(pg.sprite.Sprite):
	def __init__(self, pos):
		self.pos = pg.math.Vector2(pos)
		self.particles = []
		self.size = 64
		self.color = "pink"

	def emit(self):
		# move/draw particles
		if self.particles:
			self.deleteParticles()
			for particle in self.particles:
				#move particle
				particle[0][1] += particle[2][1]
				particle[0][0] += particle[2][0]
				#shrink particle
				particle[1] -= 0.2
				#draw circle around particle
				pg.draw.circle(pg.display.get_surface(), pg.Color(particle[3]), particle[0], int(particle[1]))

	def random_direction(self, start_angle_degrees, end_angle_degrees):
		angle_degrees = random.uniform(start_angle_degrees, end_angle_degrees)
		angle_radians = math.radians(angle_degrees)
		dx = math.cos(angle_radians) * random.randint(0,3)
		dy = math.sin(angle_radians) * random.randint(0,3)
		return dx, dy

	def addParticles(self, color="red", start_angle=None, end_angle=None, radius=6):
		self.rect = pg.Rect((self.pos.x, self.pos.y), (radius*2, radius*2))
		if start_angle is None:
			directionX = random.randint(-3,3)
			directionY = random.randint(-3,3)
		else:
			directionX, directionY = self.random_direction(start_angle, end_angle)
		particleCircle = [[self.pos.x,self.pos.y], radius, [directionX, directionY], color]
		self.particles.append(particleCircle)

	def deleteParticles(self):
		# remove particles after a certain time
		particleCopy = [particle for particle in self.particles if particle[1] > 0]
		self.particles = particleCopy

class Proto_Particle:
	def __init__(self, pos, sprite, velocity, glow=False, glow_intensity=1.0):
		self.pos = pg.Vector2(pos)
		self.sprite = sprite
		self.velocity = pg.Vector2(velocity)
		self.lifetime = 60  # Lifetime of the particle in frames
		self.glow = glow
		self.glow_intensity = glow_intensity

	def update(self):
		self.pos += self.velocity
		self.lifetime -= 1

	def draw(self, surface):
		if self.glow:
			# Create a copy of the particle's sprite with an added glow effect
			glow_sprite = self.create_glow_sprite()
			surface.blit(self.sprite, self.pos)
			surface.blit(glow_sprite, self.pos, special_flags=pg.BLEND_RGBA_MULT)
		else:
			surface.blit(self.sprite, self.pos)

	def create_glow_sprite(self):
		alpha = int(self.glow_intensity)
		glow_sprite = self.sprite.copy()
		glow_sprite.fill((255, 0, 255, alpha))
		return glow_sprite

class ParticleSystem:
	def __init__(self):
		self.particles = []

	def emit(self, pos, sprite, num_particles, direction, intensity, glow=False, glow_intensity=1.0):
		for _ in range(num_particles):
			velocity = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
			if direction == 'up':
				velocity.y -= 1
			elif direction == 'down':
				velocity.y += 1
			elif direction == 'left':
				velocity.x -= 1
			elif direction == 'right':
				velocity.x += 1
			velocity *= intensity
			particle = Particle1(pos, sprite, velocity, glow, glow_intensity)
			self.particles.append(particle)

	def update(self):
		for particle in self.particles:
			particle.update()
		self.particles = [particle for particle in self.particles if particle.lifetime > 0]

	def draw(self, surface):
		for particle in self.particles:
			particle.draw(surface)

class Particle:
    def __init__(self, x, y, direction, velocity, color):
        self.pos = [x, y]
        self.vel = [0, 0]
        self.set_direction(direction, velocity)
        self.timer = random.uniform(6, 11)
        self.color = color
        self.radius = int(self.timer)

    def set_direction(self, direction, velocity):
        if direction == "up":
            self.vel[1] = -velocity
        elif direction == "down":
            self.vel[1] = velocity
        elif direction == "left":
            self.vel[0] = -velocity
        elif direction == "right":
            self.vel[0] = velocity

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.timer -= 0.1
        self.vel[1] += 0.15
        self.radius = int(self.timer)

    def draw(self, screen):
        for i in range(self.radius, 0, -2):
            alpha = int((i / self.radius) * 255)
            color = self.color + (alpha,)
            pg.gfxdraw.aacircle(screen, int(self.pos[0]), int(self.pos[1]), i, color)
            pg.gfxdraw.filled_circle(screen, int(self.pos[0]), int(self.pos[1]), i, color)

    def is_expired(self):
        return self.timer <= 0

