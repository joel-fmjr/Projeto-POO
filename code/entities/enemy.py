import pygame
from .entity import Entity
from utils import *
from read_json import settings
from visual import GetParticle


class Enemy(Entity):
    ''' Classe responsável pela criação do inimigo e suas ações. '''

    def __init__(self, monster_name, pos, groups, obstacle_sprites, function_final, function_gameover, default_image_path, status, hitbox_inflation):

        # configuração geral
        super().__init__(groups, default_image_path, pos, status, hitbox_inflation)
        self.sprite_type = 'enemy'

        # configuração grafica
        self.__import_graphics(monster_name)
        self.animation_player = GetParticle()
        self.visible_sprites = groups[0]

        # movimento
        self.obstacle_sprites = obstacle_sprites

        # atributos
        self.monster_name = monster_name
        monster_info = settings['monster_data'][self.monster_name]
        self.health = monster_info['health']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['sight_radius']
        self.attack_type = monster_info['attack_type']

        # interação com jogador
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 800
        self.function_final = function_final
        self.function_gameover = function_gameover
        self.final_kill = None
        self.final_trigger = False
        self.deleted_time = None
        self.deleted_player = False

        # sons
        self.death_sound = pygame.mixer.Sound(
            'lib/audio/death/deleted_enemy.wav')
        self.death_sound.set_volume(0.1)
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.attack_sound.set_volume(0.1)
        self.deleted_sound = pygame.mixer.Sound('lib/audio/death/deleted.wav')
        self.deleted_sound.set_volume(0.1)

    def __import_graphics(self, name):
        ''' 
        Carrega os sprites do inimigo.
        :param name: string.
        '''
        self.animations = {'attack': [], 'walking': [], 'idle': []}
        main_path = f'lib/graphics/enemies/{name}/'
        for animation in self.animations.keys():
            full_path = main_path + animation
            self.animations[animation] = import_folder(full_path)

    def __get_player_distance_direction(self, player):
        ''' 
        Pega a direção em que o inimigo irá se mover.
        :param player: Player.
        '''
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec-enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec-enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def __get_status(self, player):
        '''
        Pega o status em que o inimigo está.
        :param player: Player
        '''
        distance = self.__get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'walking'
        else:
            self.status = 'idle'

    def __actions(self, player):
        ''' 
        Determina as ações do inimigo.
        :param player: Player.
        '''
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.__damage_player(self.attack_damage, self.attack_type, player)
            self.attack_sound.play()
        elif self.status == 'walking':
            self.direction = self.__get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        ''' Cria a animação do inimigo.'''
        animation = self.animations[self.status]

        # loop over the frame index
        self.set_frame_index(self.get_frame_index() +
                             self.get_animation_speed())
        if self.get_frame_index() >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.set_frame_index(0)

        # set the image
        self.image = animation[int(self.get_frame_index())]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        ''' Tempo de espera entre cada ação do inimigo. '''
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time >= self.get_invicible_duration():
                self.vulnerable = True
        if self.final_trigger:
            current_time = pygame.time.get_ticks()
            if current_time - self.final_kill >= 1000:
                self.function_final()
        if self.deleted_player:
            current_time = pygame.time.get_ticks()
            if current_time - self.deleted_time >= 500:
                self.kill()
                self.function_gameover()

    def get_damage(self, player):
        ''' 
        Gerencia o dano causado pelo jogador no inimigo.
        :param player: Player.
        '''
        if self.vulnerable:
            self.health -= player.attack
            if self.health <= 0:
                self.__trigger_death_particles(
                    self.rect.center, self.monster_name)
                self.death_sound.play()
                if self.monster_name == 'client':
                    self.final_kill = pygame.time.get_ticks()
                    self.final_trigger = True
                else:
                    self.kill()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
            self.direction = self.__get_player_distance_direction(player)[1]
            self.direction *= -self.resistance

    def __trigger_death_particles(self, pos, particle_type):
        '''
        Criar as animações de morte dos inimigos.
        :param pos: (int, int).
        :param particle_type: string.
        '''
        self.animation_player.create_particles(
            particle_type, pos, self.visible_sprites)

    def __damage_player(self, amount, attack_type, player):
        ''' 
        Aplica dano ao jogador e liga a invulnerabilidade temporária.
        :param amount: int.
        :param attack_type: string.
        '''
        if player.vulnerable:
            player.health -= amount
            player.vulnerable = False
            player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(
                attack_type, player.rect.center, [self.visible_sprites])
        if player.health <= 0:
            self.deleted_sound.play()
            player.kill()
            self.deleted_time = pygame.time.get_ticks()
            self.deleted_player = True

    def update(self):
        ''' Atualiza os sprites de inimigo.'''
        self.move(self.speed)
        self.animate()
        self.cooldowns()

    def enemy_update(self, player):
        '''Atualiza os parametros de inimigo que depende do jogador'''
        self.__get_status(player)
        self.__actions(player)
