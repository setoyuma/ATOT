import pygame as pg
from os import walk,sep
from csv import reader

from CONSTANTS import TILE_SIZE


def clamp(num, min_value, max_value):
	return max(min(num, max_value), min_value)

def import_folder(path) -> list:	
	surface_list = []
	for _, __, image_files in walk(path):
		for image in image_files:
			full_path = path + '/' + image
			image_surf =get_image(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_csv_layout(path) -> list:
	terrain_map = []
	with open(path) as map:
		level = reader(map, delimiter=',')
		for row in level:
			terrain_map.append(list(row))
		return terrain_map

def import_cut_graphics(path) -> list:
	surface = get_image(path)
	tile_num_x = int(surface.get_size()[0] / TILE_SIZE)
	tile_num_y = int(surface.get_size()[1] / TILE_SIZE)

	cut_tiles = []
	for row in range(tile_num_y):
		for col in range(tile_num_x):
			x = col * TILE_SIZE
			y = row * TILE_SIZE
			new_surf = pg.Surface(
				(TILE_SIZE, TILE_SIZE), flags=pg.SRCALPHA)
			new_surf.blit(surface, (0, 0), pg.Rect(
				x, y, TILE_SIZE, TILE_SIZE))
			cut_tiles.append(new_surf)

	return cut_tiles

_text_library = {}
def draw_text(surf, text, pos, size=30, color=(255,255,255), bg_color=None):
	global _text_library
	text_surf = _text_library.get(f"{text}{color}{size}")
	if text_surf is None:
		font = pg.font.Font(None, size)
		text_surf = font.render(text, True, color, bg_color)
		_text_library[f"{text}{color}{size}"] = text_surf
	x, y = pos
	surf.blit(text_surf, (x - (text_surf.get_width() // 2), y - (text_surf.get_height() // 2)))

_image_library = {}
def get_image(path):
	global _image_library
	image = _image_library.get(path)
	if image == None:
		canonicalized_path = path.replace('/', sep).replace('\\', sep)
		image = pg.image.load(canonicalized_path).convert_alpha()
		_image_library[path] = image
	return image

_sound_library = {}
def play_sound(path, stop=None):
    global _sound_library
    sound = _sound_library.get(path)
    if sound == None:
        canonicalized_path = path.replace('/', sep).replace('\\', sep)
        sound = pg.mixer.Sound(canonicalized_path)
        _sound_library[path] = sound
    if stop is None:
        sound.play()
    elif stop:
        sound.stop()
    else:
        sound.play(10)

def scale_images(images: list, size: tuple) -> list:
	""" returns scaled image assets """
	scaled_images = []
	for image in images:
		scaled_images.append(pg.transform.scale(image, size))
	return scaled_images

def text_line_wrap(surface, text, color, rect, font, aa=False, bkg=None):
	rect = pg.Rect(rect)
	y = rect.top
	lineSpacing = -2

	# get the height of the font
	fontHeight = font.size("Tg")[1]

	while text:
		i = 1

		# determine if the row of text will be outside our area
		if y + fontHeight > rect.bottom:
			break

		# determine maximum width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1

		# if we've wrapped the text, then adjust the wrap to the last word      
		if i < len(text): 
			i = text.rfind(" ", 0, i) + 1

		# render the line and blit it to the surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)

		surface.blit(image, (rect.left, y))
		y += fontHeight + lineSpacing

		# remove the text we just blitted
		text = text[i:]

	return text