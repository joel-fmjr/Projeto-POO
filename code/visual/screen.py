import pygame
from read_json import settings


class Screen:
    ''' Classe responsavel pelas telas de inicio, game hover e final. '''

    def __init__(self, screen_type, function):

        self.screen_type = screen_type
        self.display_surface = pygame.display.get_surface()
        self.img_surface = pygame.image.load(
            settings['screen_img'][screen_type])
        self.background_sound = pygame.mixer.Sound(
            'lib/audio/screen/'+screen_type+'.wav')
        self.background_sound.set_volume(0.05)
        self.function = function
        self.call_time = None
        self.call_trigger = False
        self.start_time = pygame.time.get_ticks()

    def __input(self):
        ''' Verificação se a barra de espaço foi acionado para iniciar o jogo. '''
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.screen_type == 'title':
            self.call_time = pygame.time.get_ticks()
            self.call_trigger = True

    def __cooldown(self):
        ''' Dá um tempo entre o gatilho da troca de telas para que não ocorrra de forma instantanêa. '''
        if self.call_trigger:
            current_time = pygame.time.get_ticks()
            if current_time > self.call_time + 1000:
                self.background_sound.stop()
                self.function()
        if self.screen_type != 'title':
            current_time = pygame.time.get_ticks()
            if current_time > self.start_time + 3000:
                self.background_sound.stop()
                self.function()

    def run(self):
        ''' Passa todas as funções que devem ser executadas para o loop do Game'''
        self.display_surface.blit(self.img_surface, (0, 0))
        self.background_sound.play(loops=-1, fade_ms=1)
        self.__input()
        self.__cooldown()
