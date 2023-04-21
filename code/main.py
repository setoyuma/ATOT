import pygame as pg
import sys
from settings import *
from level import Level
from game_data import levels
from pygame.locals import KEYDOWN
from button import Button
from pygame import mixer
from particle import ParticlePrinciple

# pg setup

class Game:
	def __init__(self):
		pg.init()
		mixer.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
		# self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
		pg.display.set_caption("A Tale Of Time")
		pg.display.set_icon(pg.image.load("../graphics/gameIcon.ico"))
		self.clock = pg.time.Clock()
		self.level = Level(levels[1],self.clock)

		'''sounds'''
		self.songs = {
			'title': '../audio/title/atot_title_theme.wav',
			'level_1': '../audio/title/level_1_theme.wav',
		}
		mixer.music.load(self.songs['title'])
		mixer.music.set_volume(0.7)

		'''game restart check'''
		if self.level.Player.hp <= 0:
			self.level.Player.hp = 100
			self.MainMenu()

		'''vfx'''
		self.particle1 = ParticlePrinciple()
		self.PARTICLE_EVENT = pg.USEREVENT + 1
		pg.time.set_timer(self.PARTICLE_EVENT,5)

	def Play(self):
		self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
		# self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
		mixer.music.stop()
		mixer.music.load(self.songs['level_1'])
		mixer.music.play(-1)
		pg.display.set_caption("A Tale Of Time: Crystal Song (alpha)")
		while True:
			self.screen.fill('gray')
			# self.screen.fill('#0f0024')

			for event in pg.event.get():
				if event.type == pg.QUIT:
					print('\nGame Closed\n')
					pg.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == pg.K_ESCAPE:
						self.Pause()
					if event.key == pg.K_r:
						print('\nGame Restarting...\n')
						self.__init__()
						self.Play()

				if event.type == self.PARTICLE_EVENT:
					pass
					# self.particle1.addParticles(500, 100)
					# print(f"Player Sprite X: {self.level.player.sprite.rect.x}")
					# print(f"Player Sprite Y: {self.level.player.sprite.rect.y}")

			self.level.run()
			self.particle1.emit()
			self.clock.tick(60)
			# show fps
			font = pg.font.Font(None, 30)
			fpsCounter = str(int(self.clock.get_fps()))
			text = font.render(f"FPS: {fpsCounter}", True, 'white', 'black')
			textPos = text.get_rect(centerx=1000, y=10)
			self.screen.blit(text, textPos)

			pg.display.flip()

	def MainMenu(self):
		self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
		# self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
		pg.display.set_caption("main menu")
		mixer.music.play(-1)
		while True:
			self.screen.fill('black')
			testButton = Button(SCREEN_WIDTH//2,SCREEN_HEIGHT//2,200,100,"Begin",self.Play,True,'../graphics/ui/buttons/button_plate1.png')
			for event in pg.event.get():
				if event.type == pg.QUIT:
					print('\nGame Closed\n')
					pg.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == pg.K_q:
						print('\nGame Closed\n')
						pg.quit()
						sys.exit()
					if event.key == pg.K_SPACE:
						self.Play()
			
			testButton.Process()
			self.clock.tick(60)
			# show fps
			font = pg.font.Font(None, 50)
			text = font.render("A Tale of Time: Crystal Song", True, 'white', 'black')
			textPos = text.get_rect(centerx=SCREEN_WIDTH//2, y=100)
			self.screen.blit(text, textPos)
			# print(int(clock.get_fps()))

			pg.display.flip()
	
	def Options(self):
		self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
		# self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)

		pg.display.set_caption("Options")
		vol = Button(SCREEN_WIDTH//2,SCREEN_HEIGHT//3,200,100,"Volume",self.Play,True,'../graphics/ui/buttons/button_plate1.png')
		bk = Button(SCREEN_WIDTH//2,SCREEN_HEIGHT//2,200,100,"Back",self.Pause,True,'../graphics/ui/buttons/button_plate1.png')

		while True:
			self.screen.fill('black')

			for event in pg.event.get():
				if event.type == pg.QUIT:
					print('\nGame Closed\n')
					pg.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == pg.K_ESCAPE:
						self.Pause()
			
			vol.Process()
			bk.Process()
			self.clock.tick(60)
			# show fps
			font = pg.font.Font(None, 50)
			text = font.render("Options", True, 'white', 'black')
			textPos = text.get_rect(centerx=SCREEN_WIDTH//2, y=100)
			self.screen.blit(text, textPos)

			pg.display.flip()

	def Pause(self):
		self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
		# self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
		
		pg.display.set_caption("Paused")
		buttons = [
			Button(100,0,200,100,"Resume",self.Play,True,'../graphics/ui/buttons/button_plate1.png'),
			Button(SCREEN_WIDTH - 100,0,200,100,"Options",self.Options,True,'../graphics/ui/buttons/button_plate1.png'),
			Button(100,SCREEN_HEIGHT - 100,200,100,"Exit",sys.exit,True,'../graphics/ui/buttons/button_plate1.png'),
		]

		while True:
			self.screen.fill('black')

			for event in pg.event.get():
				if event.type == pg.QUIT:
					print('\nGame Closed\n')
					pg.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == pg.K_q:
						print('\nGame Closed\n')
						pg.quit()
						sys.exit()
					if event.key == pg.K_ESCAPE:
						self.Play()
			for button in buttons:
				button.Process()
			self.clock.tick(60)
			# show fps
			font = pg.font.Font(None, 50)
			text = font.render("PAUSE", True, 'white', 'black')
			textPos = text.get_rect(centerx=SCREEN_WIDTH//2, y=100)
			self.screen.blit(text, textPos)

			pg.display.flip()


if __name__ == '__main__':
	game = Game()
	game.MainMenu()
	# game.Play()
	# game.Pause()
