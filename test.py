import pygame
import sys
from pygame.locals import *
from pygame import joystick


class ArrowGame:
    def __init__(self):
        pygame.init()

        # Create game window
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 600

        # Setup screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Input frame test")

        # Set framerate
        self.FPS = 60
        self.clock = pygame.time.Clock()

        # Load arrow images and resizes
        self.arrow_up = pygame.transform.scale(pygame.image.load('arrow_up.png'), (30, 30))
        self.arrow_down = pygame.transform.scale(pygame.image.load('arrow_down.png'), (30, 30))
        self.arrow_left = pygame.transform.scale(pygame.image.load('arrow_left.png'), (30, 30))
        self.arrow_right = pygame.transform.scale(pygame.image.load('arrow_right.png'), (30, 30))
        self.arrow_dl = pygame.transform.scale(pygame.image.load('arrow_dl.png'), (30, 30))

        # Initialize game state
        self.game_running = False
        self.game_quit = False

        # Prompt user to press spacebar to start game
        self.font = pygame.font.Font(None, 36)
        self.start_text = self.font.render("Press spacebar to start game", True, (255, 255, 255))
        self.start_text_rect = self.start_text.get_rect(center=(self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2))
        self.screen.blit(self.start_text, self.start_text_rect)
        pygame.display.update()
            


        # Initialize button combo and time since last button press
        self.button_combo = []
        self.time_since_last_button_press = 0

        # Initialize joysticks
        joystick.init()
        self.joystick = None
        if joystick.get_count() > 0:
            self.joystick = joystick.Joystick(0)
            self.joystick.init()

    def display_arrow(self, arrow):
        # Display arrow image
        arrow_rect = arrow.get_rect(center=(self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2))
        self.screen.blit(arrow, arrow_rect)
        pygame.display.flip()

        # Wait for key to be released
        while pygame.key.get_pressed()[pygame.key.get_pressed()[pygame.K_w]]:
            #check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            def check_joystick_input(self):
            # Check joystick input
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        # Get button index
                        button_index = event.button
                        # Add button index to button combo
                        self.button_combo.append(button_index)
                        # Update time since last button press
                        self.time_since_last_button_press = 0


    def run(self):
        # Wait for spacebar to start game
        while not self.game_running and not self.game_quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit == True
                    break

                # Quit the game when the window is closed
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.game_running:
                            self.game_running = True

        # Game loop
        while not self.game_quit:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit = True
                
                # Check for arrow keys being pressed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_running:
                            # Stop the game when the spacebar is pressed again
                            self.game_running = False
                            self.button_combo.clear()
                            self.time_since_last_button_press = 0
                            self.game_quit = True
                            print("Game stopped")
                    elif hasattr(event, 'key'):
                        if event.key == pygame.K_w:
                            if self.game_running:
                                self.display_arrow(self.arrow_up)
                        elif event.key == pygame.K_s:
                            if self.game_running:
                                self.display_arrow(self.arrow_down)
                        elif event.key == pygame.K_a:
                            if self.game_running:
                                self.display_arrow(self.arrow_left)
                        elif pygame.key.get_pressed()[pygame.K_s]:
                            # Check if A and S are pressed simultaneously
                            self.display_arrow(self.arrow_dl)
                        elif event.key == pygame.K_d:
                            if self.game_running:
                                self.display_arrow(self.arrow_right)
                        elif pygame.key.get_pressed()[pygame.K_s]:
                            # Check if D and S are pressed simultaneously
                            self.display_arrow(self.arrow_dl)

                        def check_joystick_input(self):
                            # Check joystick input
                                for event in pygame.event.get():
                                    if event.type == pygame.JOYBUTTONDOWN:
                                    # Get button index
                                        button_index = event.button
                                    # Add button index to button combo
                                        self.button_combo.append(button_index)
                                    # Update time since last button press
                                        self.time_since_last_button_press = 0

                                    # Show arrow image based on button pressed
                                if button_index == 0:  # Button 0 corresponds to 'up' direction on joystick
                                    self.display_arrow(self.arrow_up)
                                elif button_index == 1:  # Button 1 corresponds to 'down' direction on joystick
                                    self.display_arrow(self.arrow_down)
                                elif button_index == 2:  # Button 2 corresponds to 'left' direction on joystick
                                    self.display_arrow(self.arrow_left)
                                elif button_index == 3:  # Button 3 corresponds to 'right' direction on joystick
                                    self.display_arrow(self.arrow_right)
                                elif button_index == 4:  # Button 4 corresponds to 'down-left' direction on joystick
                                    self.display_arrow(self.arrow_dl)

                                        # Update time since last button press
                        self.time_since_last_button_press += self.clock.tick(self.FPS)

            # Update game state
            if self.game_running:
                self.time_since_last_button_press += self.clock.tick(self.FPS) / 1000
                # Check for button combo
                if self.time_since_last_button_press > 1000:
                    # Reset button combo if more than 1 second has passed
                    self.button_combo.clear()
                if pygame.key.get_pressed()[pygame.K_w]:
                    if "w" not in self.button_combo:
                        self.button_combo.append("w")
                if pygame.key.get_pressed()[pygame.K_s]:
                    if "s" not in self.button_combo:
                        self.button_combo.append("s")
                if pygame.key.get_pressed()[pygame.K_a]:
                    if "a" not in self.button_combo:
                        self.button_combo.append("a")
                if pygame.key.get_pressed()[pygame.K_d]:
                    if "d" not in self.button_combo:
                        self.button_combo.append("d")

            # Check arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.display_arrow(self.arrow_up)
            elif keys[pygame.K_s]:
                self.display_arrow(self.arrow_down)
            elif keys[pygame.K_a]:
                self.display_arrow(self.arrow_left)
            elif keys[pygame.K_d]:
                self.display_arrow(self.arrow_right)
            elif keys[pygame.K_s] and keys[pygame.K_a]:
                self.display_arrow(self.arrow_dl)
            elif keys[pygame.K_s] and keys[pygame.K_d]:
                self.display_arrow(self.arrow_dr)
            else:
                # Clear the screen if no arrow key is pressed
                self.screen.fill((255, 255, 255))

                # Check for button combo matches
                if len(self.button_combo) == 3:
                    if "w" in self.button_combo and "s" in self.button_combo and "a" in self.button_combo:
                        print("Combo: W + S + A")
                    elif "w" in self.button_combo and "s" in self.button_combo and "d" in self.button_combo:
                        print("Combo: W + S + D")

            # Draw screen
            self.screen.fill((255, 255, 255))
            if not self.game_running:
                self.screen.blit(self.start_text, self.start_text_rect)
            pygame.display.update()

        pygame.quit()
        quit()

if __name__ == "__main__":
    game = ArrowGame()
    game.run()