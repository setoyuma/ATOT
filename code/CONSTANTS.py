from BLACKFORGE2 import *
import numpy as np


notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

FPS = 60
# FPS = 30
# FPS = 10

COLORS = {
	"red"
}

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

HALF_WIDTH = SCREEN_WIDTH // 2
HALF_HEIGHT = SCREEN_HEIGHT // 2
CENTER = (HALF_WIDTH, HALF_HEIGHT)

# world
TILE_SIZE = 64
WORLD_BRIGHTNESS = 255
GRAVITY = 0.65

# path shortcuts
CHAR_PATH = '../assets/character/'
ENEMY_PATH = '../assets/enemy/'

# colors 
BG_COLOR = '#060C17'
PLAYER_COLOR = '#C4F7FF'
TILE_COLOR = '#94D7F2'

# particle datatype
particle_dtype = np.dtype([
	('position', float, (2,)),  # x, y
	('velocity', float, (2,)),  # vx, vy
	('color', float, (4,)),     # RGBA
	('size', float),            # Particle size
	('lifespan', float),        # Lifespan
	('rect', pygame.Rect)		# Rect
])

""" CHARACTER STATS """
CHARACTERS = {
	"ALRYN": {
		"SPEED": 8,
		"JUMPFORCE": 15,
	}
}

ENEMIES = {
	"sepparition": {
		"SPEED": 1,
		"GRAVITY": False,
		"HEALTH": 40,
		"AGGRO RANGE": (500,500),
	}
}

# camera
CAMERA_BORDERS = {
	'left': 400,
	'right': 400,
	'top':150,
	'bottom': 150
}

FRAME_DURATIONS = {
	'jump': 0.02,
	'fall': 0.04,
	'idle': 0.08,
	'run': .055,
	'wallJump': 0.05,
	'attack': 0.045
}
