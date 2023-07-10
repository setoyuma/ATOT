from BLACKFORGE2 import *
from CONSTANTS import *
import json


def load_save(world, player, save):
	print('loading save...\n')
	try: 
		with open("./SAVES/savedata.json", "r") as savefiles: data = json.load(savefiles)
	except: print("No Save Data...\n")
	player.rect.centerx, player.rect.centery = data[save]["X"], data[save]["Y"]
	player.position = pygame.math.Vector2(data[save]["Position"][0], data[save]["Position"][1])
	player.health = data[save]["Health"]
	player.magick = data[save]["Magick"]
	player.magick_shards = data[save]["MagickShards"]
	player.spell_shards = data[save]["SpellShards"]
	player.facing_right = data[save]["Direction"]
	player.bound_spells = data[save]["Spells"]
	player.savename = data[save]["SAVENAME"]
	print(data[save]["SAVENAME"], 'save loaded...\n')


def save_game(world, player, save):
	try: 
		with open("./SAVES/savedata.json", "r") as savefiles: data = json.load(savefiles)
	except: print("No Memory Card...\n")
	print('Saving To Memory Card...\n')
	data[save]["SAVENAME"] = player.savename
	data[save]["X"], data[save]["Y"] = player.rect.x, player.rect.y
	data[save]["Position"] = [player.position.x, player.position.y]
	data[save]["Health"] = player.health
	data[save]["Magick"] = player.magick
	data[save]["MagickShards"] = player.magick_shards
	data[save]["SpellShards"] = player.spell_shards
	data[save]["Direction"] = player.facing_right
	data[save]["Spells"] = player.bound_spells

	try: 
		with open("./SAVES/savedata.json", "w") as savefiles: json.dump(data, savefiles, indent=4)
	except: print("No Memory Card...\n")
	print(data[save]["SAVENAME"], 'Saved To Memory Card...\n')
	player.savename = data[save]["SAVENAME"]
