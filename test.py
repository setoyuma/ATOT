
		# # Check if the offset exceeds the map width
		# if self.offset.x < MAP_WIDTH//2:
		# 	self.offset.x = 0
		# elif self.offset.x > MAP_WIDTH - SCREEN_WIDTH:
		# 	self.offset.x = MAP_WIDTH - SCREEN_WIDTH
		
		# # Check if player is above or below half of the map height
		# if player.rect.centery < SCREEN_HEIGHT // 2:
		# 	self.offset.y = 0  # Lock the camera's y-offset to the top of the map
		# elif player.rect.centery > (MAP_HEIGHT - SCREEN_HEIGHT // 2):
		# 	self.offset.y = MAP_HEIGHT - SCREEN_HEIGHT  # Lock the camera's y-offset to the bottom of the map
		# else:
		# 	self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2