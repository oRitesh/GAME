import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer')

# Set fps
clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 0.75
ATTACK_COOLDOWN = 500  # Time between attacks in milliseconds
last_attack = 0

# Attack damage
ATTACK1_DAMAGE = 40
ATTACK2_DAMAGE = 25
ATTACK3_DAMAGE = 33  

# Player actions
moving_left = False
moving_right = False
attacking = False
attack_type = 0  # 1 for attack1, 2 for attack2
attack_hit_registered = False  # New flag to register only one hit per attack

# Define colours
BG = (230, 180, 193)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Load sprites
        animation_types = ['idle', 'walk', 'jump', 'attack1', 'attack2', 'attack3', 'dead']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}0.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list) 
        self.image = self.animation_list[self.action][self.frame_index]

        self.rect = self.image.get_rect()  # Hitbox
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if self.alive:  # Prevent movement while attacking
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            if moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

            # Jump
            if self.jump and not self.in_air:
                self.vel_y = -11
                self.jump = False
                self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Floor collision
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Loop animation unless it's a death animation
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 6:  # If it's the death animation, don't loop
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# Enemy class with health, gravity, and death animation
class Enemy(Character):
    def __init__(self, char_type, x, y, scale, speed, health):
        super().__init__(char_type, x, y, scale, speed)
        self.health = health
        self.disappeared = False  # New flag to check if enemy has disappeared

    def move(self):
        if self.alive:  # Only move if alive
            dy = 0
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Floor collision
            if self.rect.bottom + dy > 300:
                dy = 300 - self.rect.bottom
                self.in_air = False

            # Update rectangle position
            self.rect.y += dy

    def take_damage(self, damage):
        if self.alive:  # Only take damage if still alive
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.update_action(6)  # Trigger death animation
                print("Enemy died!")  # Debug output to confirm enemy death

    def draw_health_bar(self):
        if self.alive:  # Only show health bar if alive
            # Draw health bar
            pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 20, 50, 10))
            health_ratio = self.health / 100  # Ensure health bar scales properly
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 20, 50 * health_ratio, 10))

    def update_animation(self):
        super().update_animation()

        # Check if death animation has finished
        if not self.alive and self.frame_index == len(self.animation_list[5]) - 1:
            self.disappeared = True  # Mark as disappeared when death animation ends

    def draw(self):
        if not self.disappeared:  # Only draw enemy if not disappeared
            super().draw()

# Initialize player and enemy
player = Character('player2', 200, 200, 1, 5)
enemy = Enemy('enemy1', 400, 200, 1, 5, 100)

# Check if player is attacking enemy
def check_attack():
    global attacking, attack_type, last_attack, attack_hit_registered
    if attacking and player.alive and enemy.alive:
        # Check if player attack hits enemy and hit is not already registered for this attack
        if player.rect.colliderect(enemy.rect) and not attack_hit_registered:
            if attack_type == 1:  # Attack1 does 40 damage
                print("Attack 1 hit!")
                enemy.take_damage(ATTACK1_DAMAGE)
            elif attack_type == 2:  # Attack2 does 25 damage
                print("Attack 2 hit!")
                enemy.take_damage(ATTACK2_DAMAGE)
            elif attack_type == 3:  # Attack3 does 33 damage
                print("Attack 3 hit!")
                enemy.take_damage(ATTACK3_DAMAGE)
            attack_hit_registered = True  # Mark hit as registered for this attack

run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.draw()
    player.update_animation()

    if not enemy.disappeared:  # Only update enemy if not disappeared
        enemy.draw()
        enemy.update_animation()
        enemy.draw_health_bar()
        enemy.move()  # Apply gravity to the enemy

    # Update action
    if player.alive:
        # Check for attacking
        if attacking:
            check_attack()  # Check if attack hits the enemy

            if pygame.time.get_ticks() - last_attack > ATTACK_COOLDOWN:
                attacking = False
                attack_hit_registered = False  # Reset hit registration after attack cooldown

        if attacking:
            if attack_type == 1:
                player.update_action(3)  # Attack1
            elif attack_type == 2:
                player.update_action(4)  # Attack2
            elif attack_type == 3:
                player.update_action(5)
        elif player.in_air:
            player.update_action(2)  # Jump
        elif moving_left or moving_right:
            player.update_action(1)  # Run
        else:
            player.update_action(0)  # Idle

        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        # Quit game
        if event.type == pygame.QUIT:
            run = False
        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_q and not attacking:  # Attack1
                attacking = True
                attack_type = 1
                last_attack = pygame.time.get_ticks()
                player.update_action(3)  # 3: Attack1
            if event.key == pygame.K_e and not attacking:  # Attack2
                attacking = True
                attack_type = 2
                last_attack = pygame.time.get_ticks()
                player.update_action(4)  # 4: Attack2
            if event.key == pygame.K_r and not attacking:  # Attack3
                attacking = True
                attack_type = 3
                last_attack = pygame.time.get_ticks()
                player.update_action(5)  # 5: Attack3
            if event.key == pygame.K_ESCAPE:
                run = False
        # Keyboard release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()

pygame.quit()
