import pygame, os, time, random

pygame.font.init()

WIDTH, HEIGHT = 600, 600
player_size = (50, 50)
bullet_size = (50, 50)
bg_size = (WIDTH, HEIGHT)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shooter Tutorial')

# image loader function
def image_loader(file, size):
	return pygame.transform.scale(pygame.image.load((os.path.join('assets', file))), size)

# Load images
RED_SPACE_SHIP = image_loader('pixel_ship_red_small.png', player_size)
GREEN_SPACE_SHIP = image_loader('pixel_ship_green_small.png', player_size)
BLUE_SPACE_SHIP = image_loader('pixel_ship_blue_small.png', player_size)

# Player player
YELLOW_SPACE_SHIP = image_loader('pixel_ship_yellow.png', player_size)

# Lasers
RED_LASER = image_loader('pixel_laser_red.png', bullet_size)
GREEN_LASER = image_loader('pixel_laser_green.png', bullet_size)
BLUE_LASER = image_loader('pixel_laser_blue.png', bullet_size)
YELLOW_LASER = image_loader('pixel_laser_yellow.png', bullet_size)

# Background
BG = image_loader('background-black.png', bg_size)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
	COOLDOWN = 30

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.laser_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window): # draw beyond main
		#pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
		WIN.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()


class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
	COLOR_MAP = { 
				'red': (RED_SPACE_SHIP, RED_LASER),
				'blue': (BLUE_SPACE_SHIP, BLUE_LASER),
				'green': (GREEN_SPACE_SHIP, GREEN_LASER)
				}

	def __init__(self, x, y, color, health=100):
		super().__init__(x, y, health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))


def main():
	run = True
	FPS = 60
	level = 0
	lives = 5
	clock = pygame.time.Clock()
	main_font = pygame.font.SysFont('comicsans', 30)
	lost_font = pygame.font.SysFont('comicsans', 50)

	enemies = []
	wave_lenght = 5
	enemy_vel = 1

	lost = False
	lost_count = 0

	player_vel = 5
	laser_vel = 5

	player = Player(275, 500)

	def redraw_windows():
		WIN.blit(BG, (0,0))
		# draw text
		lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))
		level_label = main_font.render(f'level: {level}', 1, (255, 255, 255))

		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - 10 - level_label.get_width(), 10))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render('You Lost!!', 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2 - lost_label.get_height()/2))

		pygame.display.update()


	while run:
		clock.tick(FPS)
		redraw_windows()


		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		if len(enemies) == 0:
			level += 1
			wave_lenght += 5
			for i in range(wave_lenght):
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)
		

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and player.x > 0:
			player.x -= player_vel
		if keys[pygame.K_RIGHT] and player.x + player.get_width() < WIDTH:
			player.x += player_vel
		if keys[pygame.K_DOWN] and player.y + player.get_height() + 30 < HEIGHT:
			player.y += player_vel
		if keys[pygame.K_UP] and player.y > 0:
			player.y -= player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)
			elif enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(enemy)

			if random.randrange(0, 4*60) == 1:
				enemy.shoot()



		player.move_lasers(-laser_vel, enemies)

def main_menu():
	title_font = pygame.font.SysFont('comicsans', 60)
	run = True
	while run:
		WIN.blit(BG, (0,0))
		title_label = title_font.render('Press the mouse to begin...', 1, (255,255,255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2 - title_label.get_height()/2))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()

	pygame.quit()

main_menu()


