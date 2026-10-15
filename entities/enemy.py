import pygame

class Enemy:
    def __init__(self, index, total_enemies, screen_width, is_boss=False, image_path=None):
        self.is_boss = is_boss
        
        if self.is_boss:
            self.width = 120
            self.height = 100
            self.health = 5  # Boss takes 5 hits to die
            img_path = "assets/images/bigboss.png"
        else:
            self.width = 80
            self.height = 80
            self.health = 1
            img_path = image_path if image_path else "assets/images/enemy1.1.png"

        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except Exception:
            # Fallback surface if image fails to load
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 0, 0) if self.is_boss else (0, 255, 0))
            
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        if self.is_boss:
            self.target_mid_x = screen_width // 2 - self.width // 2
            self.target_mid_y = 120
            self.direction = 1  # 1 for right, -1 for left movement
        else:
            spacing = screen_width / (total_enemies + 1)
            self.target_mid_x = spacing * (index + 1) - (self.width // 2)
            self.target_mid_y = 150 + (50 if index % 2 == 0 else 0)

        self.x = self.target_mid_x
        self.y = -100

        self.state = "entering" 
        self.speed = 4
        self.dx = 0
        self.dy = 0
        self.screen_width = screen_width

    def start_drop(self, target_x, target_y):
        if self.is_boss:
            return  # Boss doesn't drop down like regular enemies
            
        self.state = "dropping"
        
        distance_x = target_x - self.x
        distance_y = target_y - self.y
        distance = (distance_x**2 + distance_y**2)**0.5

        if distance > 0:
            self.dx = (distance_x / distance) * self.speed
            self.dy = (distance_y / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed

    def update(self):
        if self.state == "entering":
            if self.y < self.target_mid_y:
                self.y += 2
            else:
                self.y = self.target_mid_y
                self.state = "waiting"

        elif self.state == "waiting":
            # Make the Big Boss move continuously left and right
            if self.is_boss:
                self.x += 2 * self.direction
                if self.x <= 50 or self.x >= self.screen_width - self.width - 50:
                    self.direction *= -1

        elif self.state == "dropping":
            self.x += self.dx
            self.y += self.dy
            
            if self.y > 650 or self.x < -100 or self.x > 900:
                self.state = "offscreen"

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (self.x, self.y))