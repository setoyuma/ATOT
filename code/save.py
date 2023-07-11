from BLACKFORGE2 import *
from CONSTANTS import *
import json


def load_save(world, player, save:str="save1"):
	print('loading save...\n')

	try: 
		with open(f"./SAVES/{save.lower()}.json", "r") as f:
			data = json.load(f)
	except FileNotFoundError as e: 
		print(f"No save file named {save.lower()}...\n", e)

	player.rect.centerx = data["X"]
	player.rect.centery = data["Y"]
	player.position = pygame.math.Vector2(data["Position"][0], data["Position"][1])
	player.health = data["Health"]
	player.magick = data["Magick"]
	player.magick_shards = data["MagickShards"]
	player.spell_shards = data["SpellShards"]
	player.facing_right = data["Direction"]
	player.bound_spells = data["Spells"]

	print(f'loaded "{save.lower()}"...\n')


def save_game(world, player, save:str="save1"):
	print('Saving to memory card...\n')

	data = {
		"X": player.rect.x, 
		"Y":  player.rect.y,
		"Position": [player.position.x, player.position.y],
		"Health": player.health,
		"Magick": player.magick,
		"MagickShards": player.magick_shards,
		"SpellShards": player.spell_shards,
		"Direction": player.facing_right,
		"Spells": player.bound_spells
	}

	try: 
		with open(f"./SAVES/{save.lower()}.json", "w") as f:
			json.dump(data, f, indent=4)
		print(f'Successfully saved to memory card slot "{save}"...\n')
	except Exception as e:
		print(f"Error saving to file: {e}\n")