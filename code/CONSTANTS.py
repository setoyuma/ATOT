notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

# screen
FPS = 60

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

HALF_WIDTH = SCREEN_WIDTH // 2
HALF_HEIGHT = SCREEN_HEIGHT // 2
CENTER = (HALF_WIDTH, HALF_HEIGHT)

# world
TILE_SIZE = 64
WORLD_BRIGHTNESS = 150
GRAVITY = 0.68

# path shortcuts
CHAR_PATH = '../assets/character/'
ENEMY_PATH = '../assets/enemy/'

# colors 
BG_COLOR = '#060C17'
PLAYER_COLOR = '#C4F7FF'
TILE_COLOR = '#94D7F2'

""" CHARACTER STATS """
CHARACTERS = {
	"ALRYN": {
		"SPEED": 7,
		"JUMPFORCE": -15,
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
	'idle': 0.05,
	'run': 0.12,
	'wallJump': 0.05,
	'attack': 0.05
}
