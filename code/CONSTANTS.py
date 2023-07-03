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
WORLD_BRIGHTNESS = 120
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
		"SPEED": 2,
		"RESIST": 3,
		"ATK_CD": 400,
		"IFRAMES": 300,
		"ATK_RAD": 200,
		"AGR_RNG": 1000,
		"ATTACKS": {'':[],'evergreen_serpent':[]},
		"GRAVITY": True,
	}
}

""" SPELLS """
SPELLS = {
	# type		 size speed damage
	'': [0, 0],
	'windblade': [96, 20, 4],
	'fireball': [64, 6, 6],
}

