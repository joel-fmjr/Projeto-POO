import pygame
from settings import *
from utils import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(
            'graphics/player/baixo/baixo_0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        # graphics setup
        self.import_player_assets()
        self.status = 'baixo'
        self.frame_index = 0
        self.animation_speed = 0.06

        # movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

    def import_player_assets(self):
        character_path = 'graphics/player/'
        self.animations = {'cima': [], 'baixo': [], 'esquerda': [], 'direita': [],
                           'direita_parado': [], 'esquerda_parado': [], 'cima_parado': [], 'baixo_parado': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        # movement input
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'cima'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'baixo'
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'direita'
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'esquerda'
        else:
            self.direction.x = 0

        # Tecla de disparo
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            pass

    def get_status(self):

        # parado status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'parado' in self.status:
                self.status = self.status + '_parado'

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def cooldowns(self):
        current_time = pygame.time.get_tick()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False

    def update(self):
        self.input()
        self.get_status()
        self.animate()
        self.move(self.speed)
