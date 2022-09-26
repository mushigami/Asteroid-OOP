import pygame, sys
from random import randint, uniform


class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        # 1. init the parent class
        super().__init__(groups)

        # timers
        self.can_shoot = True
        self.shoot_time = None
        self.duration = 500

        # 2. Surface (image)
        self.image = pygame.image.load('./graphics/ship.png').convert_alpha()

        # 3. Rect
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # 4. Mask
        self.mask = pygame.mask.from_surface(self.image)

        # 5. Sound
        self.laser_sound = pygame.mixer.Sound('./sounds/laser.ogg')

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            print("laser")
            self.shoot_time = pygame.time.get_ticks()
            Laser(self.rect.midtop, laser_group)
            self.laser_sound.play()

        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > self.duration:
                self.can_shoot = True

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            pygame.quit()
            sys.exit()

    def update(self) -> None:
        self.input_position()
        self.laser_shoot()
        self.meteor_collision()


class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.explosion_sound = pygame.mixer.Sound('./sounds/explosion.wav')


        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 300

    def meteor_collision(self):
        if pygame.sprite.groupcollide(laser_group, meteor_group, True, True, pygame.sprite.collide_mask):
            self.explosion_sound.play()

    def update(self):
        self.pos += dt * self.direction * self.speed
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.meteor_collision()

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        meteor_surf = pygame.image.load('./graphics/meteor.png').convert_alpha()
        meteor_size = pygame.math.Vector2(meteor_surf.get_size()) * uniform(0.5, 1.5)
        self.scaled_surf = pygame.transform.scale(meteor_surf, meteor_size)
        self.image = self.scaled_surf
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.speed = randint(200, 400)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)

        self.rotation = 0
        self.rotation_speed = randint(20, 100)

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += dt * self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.rotate()

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score():
    def __init__(self):
        self.font = pygame.font.Font('./graphics/subatomic.ttf', 50)

    def display(self):
        score_text = f'Score: {pygame.time.get_ticks() // 1000}'
        text_surf = self.font.render(score_text, True, 'white')
        text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, "purple", text_rect.inflate(30, 30), 5, border_radius=5)


# -----basic setup-------
pygame.init()
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Asteroid")
clock = pygame.time.Clock()
# -----basic setup-------

# -----sprites----
background_surf = pygame.image.load('./graphics/background.png').convert_alpha()
# -----sounds----
background_music = pygame.mixer.Sound('./sounds/music.wav')
background_music.set_volume(0.2)
background_music.play(loops=-1)
# -----sprite groups
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

ship = Ship(spaceship_group)
score = Score()
# -----sprites----

# -----meteor timer----
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)

# -----event loop-------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == meteor_timer:
            x_pos = randint(-100, WINDOW_WIDTH + 100)
            y_pos = randint(-100, -50)
            Meteor((x_pos, y_pos), meteor_group)

    dt = clock.tick() / 1000

    display_surface.blit(background_surf, (0, 0))
    # -----update------
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()
    score.display()

    # -----update------

    # -----collision check----
    for meteor in meteor_group:
        if meteor.rect.colliderect(ship.rect):
            print("collision")
    # -----collision check----

    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    pygame.display.update()
# -----event loop-------
