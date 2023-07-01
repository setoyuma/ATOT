from BLACKFORGE2 import *
import numpy as np


notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

FPS_SCALE = 75.0
FPS = 75
# FPS = 25
# FPS = 10


2.7 # chunks visible on screen on x axis -> SCREEN_WIDTH / ( chunk_size * TILE_SIZE)
1.5 # chunks visible on screen on y axis -> SCREEN_HEIGHT / ( chunk_size * TILE_SIZE)

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

HALF_WIDTH = SCREEN_WIDTH // 2
HALF_HEIGHT = SCREEN_HEIGHT // 2
CENTER = (HALF_WIDTH, HALF_HEIGHT)

# world
TILE_SIZE = 64
WORLD_BRIGHTNESS = 180
GRAVITY = 0.3
CHUNK_SIZE = 8

# path shortcuts
CHAR_PATH = '../assets/character/'
SPELL_PATH = '../assets/spells/' 
HITSPARK_PATH = '../assets/spells/hitsparks/' 
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

seto_colors = {
	"torch1": {
		0: [185, 60, 60], # orange
		1: [255, 0, 0], # red
		2: [250, 250, 0], # yellow
		3: [80, 50, 50], # brown
	}
}

""" CHARACTER STATS """
CHARACTERS = {
	"ALRYN": {
		"HEALTH": 100,
		"MAGICK": 50,
		"SPEED": 6,
		"JUMPS": 2,
		"JUMPFORCE": 12,
		"ROLL SPEED": 8,
		"ROLL COOLDOWN": 4,
		"DASH DIST": 30,
		"ROLL DIST": 2,
	}
}

ENEMIES = {
	"rose_sentinel": {
		"NAME": 'Rose Sentinel',
		"HEALTH": 50,
		"EXP": 6,
		'DAMAGE': 8,
		"ATTACK_TYPE": 'evergreen_serpent',
		"SPEED": 3,
		"RESIST": 3,
		"ATK_RAD": 200,
		"AGR_RNG": 50,
		"ATTACKS": {'':[],'evergreen_serpent':[]},
		"GRAVITY": True,
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
	'jump': 2,
	'fall': 4,
	'idle': 5,
	'run': 4,
	'wallJump': 5,
	'attack': 5,
	'roll': 4
}

ENEMY_FRAME_DURATIONS = {
	'rose_sentinel': {
		'move': 8,
		'attack': 8,
	}
}

# active frame data
ENEMY_FRAME_DATA = {
	'rose_sentinel': {
		'evergreen_serpent': 3,
	},
}

""" SPELLS """
SPELLS = {
	# type		 size speed
	'': [0, 0],
	'windblade': [96, 20],
	'fireball': [32, 6],
}

SPELL_FRAME_DURATIONS = {
	'windblade': 2,
	'fireball': 2,
	'wind_sparks': 3,
}

HITSPARK_FRAME_DURATIONS = {
	'fire': 6,
	'wind': 6,
}
